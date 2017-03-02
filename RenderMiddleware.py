#coding=utf-8


import random
import json
from .RenderRequest import RenderRequest,_urlencode

def render(func):
    def _wrapper(self, request, spider):

        if not isinstance(request,RenderRequest):
            return

        if not hasattr(request,'formdata_copy'):

            request.formdata_copy = request.formdata
            request.formdata = {}

        return func(self,request, spider)
    return _wrapper




class RenderUrl(object):
    """渲染Html Url"""
    def __init__(self, render_urls):
        self.render_urls = render_urls

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('RENDER_URLS'))

    @render
    def process_request(self, request, spider):
        request_url = request.url
        assert isinstance(request,RenderRequest)
        request._set_url( request.render.render_url or self._get_random_render_url() )
        request.formdata.setdefault('url',request_url)



    def _get_random_render_url(self):
        return random.choice(self.render_urls)


class RenderTime(object):
    def __init__(self,render_time):
        self.render_time = str(render_time)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('RENDER_TIME'))

    @render
    def process_request(self, request, spider):

        request.formdata.setdefault('renderTime',request.render.render_time or self.render_time)




class RenderProxy(object):
    def __init__(self,render_proxys):
        self.render_proxys = render_proxys

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('RENDER_PROXYS'))

    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('proxy',request.render.proxy or self._get_random_render_proxy())



    def _get_random_render_proxy(self):
        return random.choice(self.render_proxys)


class RenderPostParam(object):

    @render
    def process_request(self, request, spider):
        post_param = request.formdata_copy
        if not post_param:
            return
        if isinstance(post_param,dict):
            post_param = json.loads(post_param)
        request.formdata.setdefault('postParam',post_param)



class RenderUseCookie(object):

    def __init__(self,render_use_cookie):
        self.render_use_cookie = str(render_use_cookie)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('RENDER_USE_COOKIE'))

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
            items = request.formdata.items()
            querystr = _urlencode(items, request.encoding)
            request._set_body(querystr)

