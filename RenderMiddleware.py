#coding=utf-8


import random
import json
from RenderRequest import RenderRequest,_urlencode
import logging

logger = logging.getLogger(__name__)

DEFAULT_RENDER_USE_COOKIE = 0
DEFAULT_RENDER_TIME = 5000

def render(func):
    def _wrapper(self, request, spider):

        if not isinstance(request,RenderRequest):
            logger.info('request type is %s ,skip %s'%(type(request),self.__class__.__name__))
            return

        if request.not_exist_render_url:
            logger.warn('request not exist render url ,skip %s'%self.__class__.__name__)
            return

        if not hasattr(request,'formdata_copy'):
            logger.debug('copy formdata to from_copy')
            request.formdata_copy = request.formdata
            request.formdata = {}


        return func(self,request, spider)
    return _wrapper


def params_logging(func):
    def _wrapper(self ,*args,**kwargs):
        log = """%s init params:"""%(self.__class__.__name__,)
        if args:
            log += '\n'.join(map(str,args))
        if kwargs:
            log += '\n'.join(map(str,kwargs.values()))
        logger.debug(log)
        return func(self,*args,**kwargs)
    return _wrapper



class RenderUrlsNullError(Exception):
    pass

class RenderUrl(object):

    @params_logging
    def __init__(self, render_urls):
        if not render_urls:
            raise RenderUrlsNullError,'render urls unknown'

        self.render_urls = render_urls

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('RENDER_URLS',))

    @render
    def process_request(self, request, spider):
        request_url = request.url
        render_url = request.render.render_url or self._get_random_render_url()
        if not render_url:
            request.not_exist_render_url = True
            return

        request._set_url( render_url )
        request.formdata.setdefault('url',request_url)



    def _get_random_render_url(self):
        return random.choice(self.render_urls)


class RenderTime(object):
    @params_logging
    def __init__(self,render_time):
        self.render_time = str(render_time)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('RENDER_TIME',DEFAULT_RENDER_TIME))

    @render
    def process_request(self, request, spider):

        request.formdata.setdefault('renderTime',request.render.render_time or self.render_time)




class RenderProxy(object):

    @params_logging
    def __init__(self,render_proxys):
        self.render_proxys = render_proxys

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('RENDER_PROXYS',['',]))

    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('proxy',request.render.proxy or self._get_random_render_proxy())



    def _get_random_render_proxy(self):
        render_proxy = random.choice(self.render_proxys)
        if not render_proxy:
            logger.warn('render_proxy is null ,use null')
            return ''

        return render_proxy


class RenderPostParam(object):

    @render
    def process_request(self, request, spider):
        post_param = request.formdata_copy
        if not post_param:
            logger.debug('request post fromdata is null')
            return

        if isinstance(post_param,dict):
            logger.debug('request post fromdata to json')
            post_param = json.loads(post_param)
        request.formdata.setdefault('postParam',post_param)



class RenderUseCookie(object):

    @params_logging
    def __init__(self,render_use_cookie):
        self.render_use_cookie = str(render_use_cookie)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('RENDER_USE_COOKIE',DEFAULT_RENDER_USE_COOKIE))

    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('useCookie',request.render.use_cookie or self.render_use_cookie)


class RenderContentType(object):
    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('contentType',request.render.content_type)



class RenderScript(object):
    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('script',request.render.script)



class RenderUserAgent(object):

    @params_logging
    def __init__(self,render_user_agents):
        self.render_user_agents = render_user_agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('RENDER_USER_AGENTS'))


    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('ua',request.render.user_agent or self._get_random_render_user_agent() )



    def _get_random_render_user_agent(self):
        return {'User-Agent':random.choice(self.render_user_agents)}





class RenderBody(object):

    @render
    def process_request(self, request, spider):
        if request.formdata:
            logger.debug('encoding formdata')
            items = request.formdata.items()
            querystr = _urlencode(items, request.encoding)
            request._set_body(querystr)

