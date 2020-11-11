import os

from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.response import Response
from django.views import View
from django.views.generic import TemplateView
from google_play_scraper import app
from bs4 import BeautifulSoup


def get_url(search_keyword):
    app_name_split = search_keyword.split(' ')
    url_app_query = app_name_split[0]
    if len(app_name_split) > 1:
        for _ in range(1, len(app_name_split)):
            url_app_query = url_app_query + '%20{}'.format(app_name_split[_])
    url = "https://play.google.com/store/search?q={}&c=apps".format(url_app_query)
    return url


def get_search_list(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    class_results = soup.find_all('div', class_='b8cIId ReQCgd Q9MA7b')
    app_id_list = []
    for _ in class_results:
        app_id = _.find('a')['href'].split('?id=')[1]
        app_id_list.append(app_id)
    return app_id_list


def get_contact_information(app_id_list, lang='en', country='us'):
    result = {}
    for app_id in app_id_list:
        response = app(app_id, lang=lang, country=country)

        app_result = {
            "developer: " + str(response['developer']),
            "developerId: " + str(response['developerId']),
            "developerEmail: " + str(response['developerEmail']),
            "developerWebsite: " + str(response['developerWebsite']),
            "developerAddress: " + str(response['developerAddress']),
            "developerInternalID: " + str(response['developerInternalID'])
        }
        result[app_id] = app_result
    return result


class TestView(View):
    def get(self, request, *args, **kwargs):
        print(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        return Response({'message': 'ok report'}, status=200, )


class SearchBarView(TemplateView):
    template_name = 'search_bar.html'


class GetContactInformation(View):

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        url = get_url(q)
        print('Fetching results for url: {}'.format(url))
        id_list = get_search_list(url)
        print('Total {} results found'.format(len(id_list)))
        results = get_contact_information(id_list)
        return render(request, 'search_results.html', {'results': results})
