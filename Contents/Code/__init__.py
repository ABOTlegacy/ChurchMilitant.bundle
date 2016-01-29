RE_SEASON_EP = Regex('Season (?P<season>\d+), Ep. (?P<episode>\d+)')


URL_ROOT = 'http://www.churchmilitant.com'
URL_REPORTS      = 'http://www.churchmilitant.com/search/ajax-results/eyJjaGlsZDp2aWRlb19zZXJpZXMiOiIxODQiLCJjaGFubmVsIjoiZGF0ZWRfdmlkZW8iLCJyZXN1bHRfcGFnZSI6InNlYXJjaFwvYWpheC1yZXN1bHRzIn0'
URL_THE_VORTEX   = 'http://www.churchmilitant.com/search/ajax-results/eyJjaGlsZDp2aWRlb19zZXJpZXMiOiIxODYiLCJjaGFubmVsIjoiZGF0ZWRfdmlkZW8iLCJyZXN1bHRfcGFnZSI6InNlYXJjaFwvYWpheC1yZXN1bHRzIn0'
URL_HEADLINES    = 'http://www.churchmilitant.com/search/ajax-results/eyJjaGlsZDp2aWRlb19zZXJpZXMiOiIxODciLCJjaGFubmVsIjoiZGF0ZWRfdmlkZW8iLCJyZXN1bHRfcGFnZSI6InNlYXJjaFwvYWpheC1yZXN1bHRzIn0'
URL_THE_DOWNLOAD = 'http://www.churchmilitant.com/search/ajax-results/eyJjaGlsZDp2aWRlb19zZXJpZXMiOiIxODkiLCJjaGFubmVsIjoiZGF0ZWRfdmlkZW8iLCJyZXN1bHRfcGFnZSI6InNlYXJjaFwvYWpheC1yZXN1bHRzIn0'
URL_MICD_UP      = 'http://www.churchmilitant.com/search/ajax-results/eyJjaGlsZDp2aWRlb19zZXJpZXMiOiIxODMiLCJjaGFubmVsIjoiZGF0ZWRfdmlkZW8iLCJyZXN1bHRfcGFnZSI6InNlYXJjaFwvYWpheC1yZXN1bHRzIn0'


####################################################################################################
def Start():

    ObjectContainer.title1 = 'Church Militant'

####################################################################################################
@handler('/video/churchmilitant', 'Church Militant')
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(
        key = Callback(Episodes, url=URL_HEADLINES, title="Headlines"),
        title = "Headlines",
        thumb = "http://www.churchmilitant.com/images/uploads/series_banners/news_pa.jpg"
    ))

    oc.add(DirectoryObject(
        key = Callback(Episodes, url=URL_REPORTS, title="Reports"),
        title = "Reports",
        thumb = "http://www.churchmilitant.com/images/uploads/series_banners/repo_pa.png"
    ))

    oc.add(DirectoryObject(
        key = Callback(Episodes, url=URL_THE_VORTEX, title="The Vortex"),
        title = "The Vortex",
        thumb = "http://www.churchmilitant.com/images/uploads/series_banners/vort_pa.png"
    ))

    return oc

####################################################################################################
@route('/video/churchmilitant/episodes')
def Episodes(url, title):

    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)

    for item in html.xpath('//div[@class="col-xs-2 item"]/a'):
        episode_url = item.xpath('./@href')[0]
        if not episode_url.startswith('http://'):
            if not episode_url.startswith('https://'):
                episode_url = '%s%s' % (URL_ROOT, url)

        thumb = item.xpath('./div[@class="video-thumb-wrapper"]/img/@data-original')[0]
        if not thumb.startswith('http://'):
            if not thumb.startswith('https://'):
                thumb = '%s%s' % (URL_ROOT, thumb)

        episode_title = item.xpath('./div[@class="video-sm-title"]/text()')[0]


        episode = {}
        episode['episode_url'] = episode_url
        episode['thumb'] = thumb
        episode['show_title'] = title
        episode['episode_title'] = episode_title
        episode['index'] = len(oc) + 1
        episode['summary'] = None
        episode['video_list'] = []

        oc.add(
            CreateVideoClipObject(episode)
        )

  
    return oc


###################################################################################################
def CreateVideoClipObject(episode, include_container=False):


    if include_container:
        # Obtain the Video HTML
        HTTP_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1',
            'Referer': 'http://www.churchmilitant.com/'
        }
        html_page = HTML.ElementFromURL(episode['episode_url'])
        html_page_video = HTTP.Request(html_page.xpath('//iframe[@allowfullscreen]/@src')[0], headers=HTTP_HEADERS).content
        
        # Parse for MP4 File
        video_url_720p = Regex('(?<=width":1280)(.*)(?=quality":"720p)').search(html_page_video)
        if video_url_720p:
            video_url_720p = Regex("(https:)([/|.|\w|\s]|-)*(?:mp4)((\w|\s|&|=|\?)*)").search(video_url_720p.group(0))
            if video_url_720p:
                video_url_720p = video_url_720p.group(0)
                episode['video_list'] = video_url_720p

        # Go Into The Page
        #html_page = HTML.ElementFromURL(episode['episode_url'])
        #episode['summary'] = html_page.xpath('//iframe/@title')[0]



    videoclip_obj = EpisodeObject(
        key=Callback(CreateVideoClipObject, episode=episode, include_container=True),
        rating_key=episode['index'],
        title=episode['episode_title'],
        summary=episode['summary'],
        thumb=Resource.ContentsOfURLWithFallback(episode['thumb']),
        #art=image,
        index=episode['index'],
        items=[
            MediaObject(
                parts=[PartObject(key=episode['video_list'])],
                container=Container.MP4,
                video_resolution='720'
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[videoclip_obj])
    else:
        return videoclip_obj