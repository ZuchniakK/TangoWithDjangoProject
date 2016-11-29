from googleapiclient.discovery import build
from tango_with_django_project.settings import GOOGLE_SEARCH_API_KEY, GOOGLE_ENGINE_ID


def google_search(query, search_num):
    service = build("customsearch", "v1",
                    developerKey=GOOGLE_SEARCH_API_KEY)
    print('start')
    res = service.cse().list(
        q=query,
        cx=GOOGLE_ENGINE_ID,
        num=search_num
    ).execute()
    print('cokolwiek')
    print(res)
    print(res['queries'])
    print(res['queries']['request'][0])
    print(res['queries']['request'][0]['totalResults'])

    results = []
    if not res['queries']['request'][0]['totalResults'] == '0':
        for result in res['items']:
            results.append({'title': result['title'],
                            'link': result['link'],
                            'summary': result['snippet']})

    return results

if __name__ == '__main__':
    search_1 = google_search('borsuk' , 5)
    print(search_1[4]["link"])