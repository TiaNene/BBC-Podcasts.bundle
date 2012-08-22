import re

####################################################################################################

BBCPODCASTS_URL         = "http://www.bbc.co.uk/podcasts"
BBC_URL                 = "http://www.bbc.co.uk"
BBCPODCASTS_SEARCH_URL  = "http://www.bbc.co.uk/podcasts/quick_search/"
BBCPODCASTS_SERIES_URL  = "http://www.bbc.co.uk/podcasts/series/"
BBCPODCASTS_IMAGE_URL   = "http://www.bbc.co.uk/podcasts/assets/artwork/266/%s.jpg"

DEBUG_XML_RESPONSE		= False
CACHE_INTERVAL          = 1800 # These cache times are relatively short since the pages change fairly frequently
CACHE_RSS_FEED_INTERVAL = 1800
CACHE_SEARCH_INTERVAL	= 600

ITUNES_NAMESPACE = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'}

ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler('/music/bbcpodcasts', Browser, L('bbcpodcasts'), ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
  MediaContainer.content = 'Items'
  MediaContainer.art = R(ART)
  MediaContainer.title1 = L('bbcpodcasts')
  MediaContainer.viewGroup = 'List'
  DirectoryItem.thumb = R(ICON)
  HTTP.CacheTime = CACHE_INTERVAL

# No UpdateCache method is used, as this would only be useful for 'editors picks' / 'recently added' 
# And even for those pages the delay in fetching a single page is relatively short

def Browser(sender=False, topLevel=True, stationId=None, stationName=None, genreId=None, genreName=None, order=None, selector=None, pageNumber=None, title1=None, title2=None):

  dir = MediaContainer()

  # Since Browser is called from a variety of places it should be called with appropriate titles to use

  if title1:
    dir.title1 = title1

  if title2:
    dir.title2 = title2

  # The url for the page is a built from the filters we currently have

  url = BBCPODCASTS_URL

  if stationId:
    url += "/" + stationId

  if genreId:
    url += "/genre/" + genreId

  if order and order != 'lastupdated':
    url += "/" + order

  if pageNumber:
    url += "?page=" + pageNumber

  url += "/"

  if selector:

    page = HTML.ElementFromURL(url, cacheTime=CACHE_INTERVAL)

    # We need to display a choice of either stations or genres

    if selector=='filterstation':
      options = page.xpath("//div[@id='pc-filter-networks']/ul/li/a[not(@class='pc-filter-empty')]") 
    else: # filtergenre
      options = page.xpath("//div[@id='pc-filter-genres']/ul/li/a[not(@class=' pc-filter-empty')]") # Note the space before pc-filter-empty

    for option in options:

      optionName = str(option.xpath("./text()")[0])
      url = option.get('href')

      if selector=='filterstation':

        optionId = re.search(r'^/podcasts/([^/]+)', url).group(1)
        dir.Append(Function(DirectoryItem(Browser, title=optionName, summary='', subittle='', thumb=Function(GetThumb, url=L(optionName))), topLevel=False, stationId=optionId, stationName=optionName, genreId=genreId, genreName=genreName, order=order, selector=None, title1=title2, title2=optionName))

      else: # filtergenre

        optionId = re.search(r'/genre/([^/]+)', url).group(1)
        dir.Append(Function(DirectoryItem(Browser, title=optionName, summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=optionId, genreName=optionName, order=order, selector=None, title1=title2, title2=optionName))

  elif not order:

    # No order is slected, present the options

    if topLevel:
       # Show the highlights on the top level menu
       dir.Append(Function(DirectoryItem(BrowseHighlights, title=L('editorspicks'), summary='', subtitle=''), highlightCategory='editorspicks'))
       dir.Append(Function(DirectoryItem(BrowseHighlights, title=L('recentlylaunched'), summary='', subtitle=''), highlightCategory='recentlylaunched'))


    if not stationId:
      dir.Append(Function(DirectoryItem(Browser, title=L('filterstation'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order=None, selector='filterstation', title1=title2, title2=L('filterstation')))

    if not genreId:
      dir.Append(Function(DirectoryItem(Browser, title=L('filtergenre'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order=None, selector='filtergenre', title1=title2, title2=L('filtergenre')))


    dir.Append(Function(DirectoryItem(Browser, title=L('lastupdated'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order='lastupdated', selector=None, title1=title2, title2=L('lastupdated')))
    dir.Append(Function(DirectoryItem(Browser, title=L('a-z'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order='a-z', selector=None, title1=title2, title2=L('a-z')))
    dir.Append(Function(DirectoryItem(Browser, title=L('z-a'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order='z-a', selector=None, title1=title2, title2=L('z-a')))
    dir.Append(Function(DirectoryItem(Browser, title=L('duration_desc'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order='duration_desc', selector=None, title1=title2, title2=L('duration_desc')))
    dir.Append(Function(DirectoryItem(Browser, title=L('duration_asc'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order='duration_asc', selector=None, title1=title2, title2=L('duracion_asc')))

    if topLevel:
      # This is the top level menu, show the search entry
      dir.Append(Function(SearchDirectoryItem(Search, title=L('search'), prompt=L('searchprompt'), thumb=R('icon-search.png'))))



  else:

    # An order is selected (eg a-z), show the availale podcasts

    dir.viewGroup = 'InfoList'

    page = HTML.ElementFromURL(url, cacheTime=CACHE_INTERVAL)

    podcasts = page.xpath("//div[@class='pc-results-box']")

    for podcast in podcasts:

      podcastName = TidyString(podcast.xpath("./div[@class='pc-results-box-data']/h2/a/text()")[0])
      podcastUrl = BBC_URL + podcast.xpath("./div[@class='pc-results-box-data']/h2/a")[0].get('href')
      podcastImage = podcast.xpath("./div[@class='pc-results-box-artwork']/a/img")[0].get('src')
      podcastImage = re.sub(r'/84/', r'/266/', podcastImage)

      podcastLastUpdated = podcast.xpath("./div[@class='pc-results-box-data']/div[@class='pc-result-episode']/p[@class='pc-result-episode-date']/strong/text()")[0] 
      podcastAverageDuration = podcast.xpath("./div[@class='pc-results-box-data']/div[@class='pc-result-episode']/p[@class='pc-result-episode-duration']/strong/text()")[0]

      podcastGlobalAvailability = ''

      if len(podcast.xpath("./div[@class='pc-results-box-data']/p[@class='pc-result-uk']")) > 0:
        podcastGlobalAvailability = L('ukonly')
      else:
        podcastGlobalAvailability = L('worldwide')

      podcastSubtitle = ''

      if podcastLastUpdated == 'No episodes available':
        podcastSubtitle = podcastLastUpdated + "\n" + L('averagelength') + ": " + podcastAverageDuration
      else: 
        podcastSubtitle = L('updateddate') + ": " + podcastLastUpdated + "\n" + L('averagelength') + ": " + podcastAverageDuration

      podcastDescription = ''

      # Try to find extra metadata from the 'Glow' fields

      podcastShortTitle = re.search('series\/(.*)$', podcastUrl).group(1)
      glowPanels = podcast.xpath("//div[@id='pc-further-r_" + podcastShortTitle + "']")

      if len(glowPanels):

        glowPanel = glowPanels[0]

        # Description is the text in the info panel, and sub elements (...)

        descriptionBox = glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='results-box-description']")[0]
        podcastDescription = "\n\n\n\n" + descriptionBox.xpath("./text()")[0]

        descriptionChildren = descriptionBox.xpath("./*")
        if len (descriptionChildren) > 0:
          for child in descriptionChildren:
            # Test if child has text
            if len(child.xpath("./text()")) > 0:
              podcastDescription += child.xpath("./text()")[0]

        podcastFrequency = glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='results-box-frequency']/text()")[0]
        podcastNumberAvailable = glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='results-box-available']/text()")[0]

        podcastSubtitle = podcastGlobalAvailability + "\n" + podcastSubtitle + "\n" + L('frequency') + ": " + podcastFrequency + "\n" + L('availability') + ": " + podcastNumberAvailable

      dir.Append(Function(DirectoryItem(ShowPodcast, title=podcastName, summary=podcastDescription, subtitle=podcastSubtitle, thumb=Function(GetThumb, url=podcastImage)), podcastName=podcastName, podcastUrl=podcastUrl, podcastImage=podcastImage, title1=title2))


    # See if we have multiple pages
    nextLinks = page.xpath("//li[@class='nav-pages-next']/a")

    if len(nextLinks) > 0:

      # We have a next page link
      nextPageUrl = nextLinks[0].get('href')
      nextPageNumber = re.search(r'page=(\d+)$', nextPageUrl).group(1)

      dir.Append(Function(DirectoryItem(Browser, title=L('nextpage'), summary='', subittle=''), topLevel=False, stationId=stationId, stationName=stationName, genreId=genreId, genreName=genreName, order=order, selector=None, pageNumber=nextPageNumber))



  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir



def BrowseHighlights(sender, highlightCategory):

  # Browse either the Editors Picks or Recently Launched

  dir = MediaContainer(viewGroup = 'InfoList', title2 = L(highlightCategory))

  url = BBCPODCASTS_URL + "/"

  page = HTML.ElementFromURL(url, cacheTime=CACHE_INTERVAL)

  if highlightCategory == 'editorspicks':
    podcasts = page.xpath("//div[@id='pc-promo-editors']/div[@class='pc-promo-item']")
  else:
    podcasts = page.xpath("//div[@id='pc-promo-recent']/div[@class='pc-promo-item']")

  for podcast in podcasts:

    podcastUrl = BBC_URL + podcast.xpath("./p/a")[0].get('href')

    podcastShortTitle = re.search('series\/(.*)$', podcastUrl).group(1)
    podcastImage = BBCPODCASTS_IMAGE_URL % podcastShortTitle
    podcastDescription = ''
    podcastSubtitle = ''
    podcastName = ''


    if highlightCategory == 'editorspicks':
      glowPanels = podcast.xpath("//div[@id='pc-further-p_edi_" + podcastShortTitle + "']")
    else:
      glowPanels = podcast.xpath("//div[@id='pc-further-p_rec_" + podcastShortTitle + "']")


    if len(glowPanels):
      glowPanel = glowPanels[0]

      podcastName = TidyString(glowPanel.xpath("./div[@class='pc-infopanel']/h3/text()")[0])
      podcastDescription = "\n\n" + TidyString(glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='results-box-description']/text()")[0])
      podcastEpisodeDate = TidyString(glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='pc-result-episode-date']/text()")[0])
      podcastDuration = TidyString(glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='pc-result-episode-duration']/text()")[0])

      podcastGlobalAvalability = ''
      if len(glowPanel.xpath("./div[@class='pc-infopanel']/p[@class='pc-promo-ukonly']")) > 0:
        podcastGlobalAvailability = L('ukonly')
      else:
        podcastGlobalAvailability = L('worldwide')

      podcastSubtitle = podcastGlobalAvailability + "\n" + L('updateddate') + ": " + podcastEpisodeDate + "\n" + L('averagelength') + ": " + podcastDuration

    dir.Append(Function(DirectoryItem(ShowPodcast, title=podcastName, summary=podcastDescription, subtitle=podcastSubtitle, thumb=Function(GetThumb, url=podcastImage)), podcastName=podcastName, podcastUrl=podcastUrl, podcastImage=podcastImage, title1=L(highlightCategory)))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir




def ShowPodcast(sender, podcastName=None, podcastUrl=None, podcastImage=None, title1=None):

  dir = MediaContainer(viewGroup = 'InfoList', title2 = podcastName)
  if title1:
    dir.title1 = title1

  page = HTML.ElementFromURL(podcastUrl, cacheTime=CACHE_INTERVAL)

  if len ( page.xpath("//div[@id='pc-help-why']") ) > 0:

    # Podcast is not available to the user as they are outside the UK.
    return (MessageContainer(header=L('notavailable'), message=L('notoutsideuk')))


  else:

    # Retrive RSS Link from podcast page
    rssUrl = page.xpath("//div[@id='pc-subscribe-buttons']/ul/li[@id='pc-sublink-rss']/a")[0].get('href')
  #  rssUrl = page.xpath("//li[@id='pc-sublink-rss']/a")[0].get('href')

    rss = XML.ElementFromURL(rssUrl, cacheTime=CACHE_RSS_FEED_INTERVAL)

    episodes = rss.xpath("//channel/item")

    if len(episodes):

      for episode in episodes:

        episodeUrl = episode.xpath("./enclosure")[0].get('url')
        episodeTitle = episode.xpath("./title/text()")[0]
        episodeDate = str(episode.xpath("./pubDate/text()")[0])
        episodeDescription = episode.xpath("./description/text()")[0]
        episodeSubtitle = episodeDate

        episodeLength = 0
        if len(episode.xpath("./itunes:duration/text()", namespaces=ITUNES_NAMESPACE)) > 0:
          episodeLength = episode.xpath("./itunes:duration/text()", namespaces=ITUNES_NAMESPACE)[0]
          # Formatting is either 'seconds' 'hh:mm:ss' or 'mm:ss'
          if re.search(r':', episodeLength):
            episodeLengthParts = re.search(r'((\d*):)?(\d+):(\d+)', episodeLength)
            if episodeLengthParts.group(2) is not None:
              # Time has hours minutes and seconds
              episodeLengthSeconds = (int(episodeLengthParts.group(2)) * 3600 )+ ( int(episodeLengthParts.group(3)) * 60 ) +  int(episodeLengthParts.group(4))
            else:
              # Time has just minutes and seconds
              episodeLengthSeconds = int(episodeLengthParts.group(3)) * 60  +  int(episodeLengthParts.group(4))
          else:
            episodeLengthSeconds = int(episodeLength)
          episodeLength = str(episodeLengthSeconds * 1000)


        dir.Append(TrackItem(episodeUrl, episodeTitle, artist=podcastName, album=L('bbcpodcasts'), summary=episodeDescription, subtitle=episodeSubtitle, duration=episodeLength, thumb=Function(GetThumb, url=podcastImage))) 


      if DEBUG_XML_RESPONSE:
        Log(dir.Content())
      return dir

    else:

      # No episodes currently available for the podcast

      return (MessageContainer(header=L('bbcpodcasts'), message=L('noepisodes')))



def Search(sender, query):

  dir = MediaContainer(title2 = L('searchresults'))

  query = query.replace(' ', '_')

  jsonResults = JSON.ObjectFromURL(BBCPODCASTS_SEARCH_URL + query, cacheTime=CACHE_SEARCH_INTERVAL)

  # Stip the results so they only contain podcasts (and not genre links)

  results = []

  for result in jsonResults:
    if result.has_key("fullTitle"):
      results.append(result)

  if len(results):

    # Results were returned

    for result in results:

      if result.has_key("fullTitle"):

        podcastName = result['fullTitle']
        shortTitle = result['shortTitle']

        podcastUrl = BBCPODCASTS_SERIES_URL + shortTitle 
        podcastImage = BBCPODCASTS_IMAGE_URL % shortTitle

        dir.Append(Function(DirectoryItem(ShowPodcast, title=podcastName, summary='', subtitle='', thumb=Function(GetThumb, url=podcastImage)), podcastName=podcastName, podcastUrl=podcastUrl, podcastImage=podcastImage, title1=L('searchresults')))

    if DEBUG_XML_RESPONSE:
      Log(dir.Content())
    return dir

  else:

    # No results returned

    return (MessageContainer(header=L('searchresults'), message=L('searchnoresults')))



############################

def TidyString(stringToTidy):
  # Function to tidy up strings works ok with unicode, 'strip' seems to have issues in some cases so we use a regex
  if stringToTidy:
    # Strip new lines
    stringToTidy = re.sub(r'\n', r' ', stringToTidy)
    # Strip leading / trailing spaces
    stringSearch = re.search(r'^\s*(\S.*?\S?)\s*$', stringToTidy)
    if stringSearch == None:
      return ''
    else:
      return stringSearch.group(1)
  else:
    return ''

############################

def GetThumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    pass

  return Redirect(R(ICON))
