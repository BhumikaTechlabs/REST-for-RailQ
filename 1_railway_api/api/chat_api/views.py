from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from . import models
from . import serializers
from . import forms
import requests
from django.db.models import Q

class MessageListView(generics.ListCreateAPIView):
    #queryset = models.Message.objects.all()
    #serializer_class = serializers.MessageSerializer

    # get all msgs of userid passed as request parameter
	@api_view(['GET'])
	def msg_history(request):
		queryset = models.Message.objects.all().filter(Q(userid=request.GET['userid']))
		serializer = serializers.MessageSerializer(queryset, many=True)
		return Response(serializer.data)

class MForm(generics.CreateAPIView):
	#serializer_class = serializers.MessageSerializer

	# post a msg as request parameter and get bot response
	@api_view(['GET','POST'])
	def invokeBot(request):
		umsg = request.GET['msg']
		# api call to Dialogflow
		url = "https://api.dialogflow.com/v1/query?v=20150910&lang=en&query="+umsg+"&sessionId=22222"
		headers = {'Authorization' : 'Bearer def009d7b99046678c492c0499e1f2ca'}
		r = requests.get(url, headers=headers)
		mjson = r.json()
		botReply = mjson['result']['fulfillment']['speech']
		srcStation =  mjson.get('result').get('parameters').get('sourceStation','')
		destnStation =  mjson.get('result').get('parameters').get('destinationStation','')
		travelDate =  mjson.get('result').get('parameters').get('travelDate','')
		mjson = ""
		# if all parameter values have been received, make api call to railwayapi
		if srcStation != '' and destnStation != '' and travelDate != '':
			# ---- some data pre-processing & formattind ----
			# get src station code by src station name
			url = "http://api.railwayapi.com/v2/name-to-code/station/"+srcStation+"/apikey/pi9h941fgc/"
			r = requests.get(url)
			mjson = r.json()
			srcCode = mjson['stations'][0]['code']
			# get dstn station code by dstn station name
			url = "http://api.railwayapi.com/v2/name-to-code/station/"+destnStation+"/apikey/pi9h941fgc/"
			r = requests.get(url)
			mjson = r.json()
			destnCode = mjson['stations'][0]['code']
			# format the travel date returned by bot
			# because: dialogflow returns yyyy-mm-dd
			# but, railwayapi needs dd-mm-yyyy
			yyyy = travelDate[:4]
			mm = travelDate[5:7]
			dd = travelDate[8:10]
			tDate = dd+"-"+mm+"-"+yyyy
			# --------------
			#get train info as per parameters
			url = "http://api.railwayapi.com/v2/between/source/"+srcCode+"/dest/"+destnCode+"/date/"+tDate+"/apikey/pi9h941fgc/"
			r = requests.get(url)
			mjson = r.text

		return Response(botReply+'<br/>'+mjson)
