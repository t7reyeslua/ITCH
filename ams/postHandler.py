import requests
import json
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
import logging

logger = logging.getLogger('django.request')
import concurrent.futures

# Create your views here.
class PostHandler(APIView):

    def post(self, request, return_dict=False):
        if return_dict == False:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request
        command = data.get('content', None)
        if command:
            logger.debug(command)

            #TODO handle post request
            post_response = {'response': 'post_handler'}

            if return_dict:
                return post_response
            return JsonResponse(post_response)
        if return_dict:
            return {'error': True, 'message': 'unknown request'}
        return JsonResponse({'error': True, 'message': 'unknown request'})



