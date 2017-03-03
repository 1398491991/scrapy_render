#coding=utf-8
from RenderMiddleware import RenderBody,render,params_logging
import redis
import logging

logger = logging.getLogger(__name__)

DEFAULT_RENDER_REDIS_URLS_KEY = 'scrapy_render:render_redis_urls'
DEFAULT_REDIS_CONN_CONFIG = {}
DEFAULT_RENDER_REDIS_TIME = 5000
DEFAULT_RENDER_REDIS_TIME_KEY = 'scrapy_render:render_redis_time'
DEFAULT_RENDER_REDIS_PROXYS_KEY = 'scrapy_render:render_redis_proxys'
DEFAULT_RENDER_REDIS_USE_COOKIE_KEY = 'scrapy_render:render_redis_use_cookie'
DEFAULT_RENDER_REDIS_USE_COOKIE = 0


class RenderRedisUrlNullError(Exception):
    pass

class RenderRedisBody(RenderBody):
    pass


class RenderRedisBase(object):
    def __init__(self,redis_conn_config):
        self.server = redis.Redis(**redis_conn_config)


class RenderRedisUrl(RenderRedisBase):

    @params_logging
    def __init__(self, redis_conn_config,render_redis_urls_key):
        super(RenderRedisUrl,self).__init__(redis_conn_config)
        if not self.server.exists(render_redis_urls_key):
            raise RenderRedisUrlNullError,'render urls unknown , redis key: %s'%render_redis_urls_key

        self.render_redis_urls_key = render_redis_urls_key



    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict('REDIS_CONN_CONFIG',DEFAULT_REDIS_CONN_CONFIG),
                   crawler.settings.get('RENDER_REDIS_URLS_KEY',DEFAULT_RENDER_REDIS_URLS_KEY)
                   )

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
        return self.server.srandmember(self.render_redis_urls_key)



class RenderRedisTime(RenderRedisBase):

    @params_logging
    def __init__(self, redis_conn_config,render_redis_time_key,
                 default_render_redis_time):
        super(RenderRedisTime,self).__init__(redis_conn_config)
        self.render_redis_time_key = render_redis_time_key
        self.default_render_redis_time = str(default_render_redis_time)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict('REDIS_CONN_CONFIG',DEFAULT_REDIS_CONN_CONFIG),
                   crawler.settings.get('RENDER_REDIS_TIME_KEY',DEFAULT_RENDER_REDIS_TIME_KEY),
                   crawler.settings.get('DEFAULT_RENDER_REDIS_TIME',DEFAULT_RENDER_REDIS_TIME))

    @render
    def process_request(self, request, spider):

        request.formdata.setdefault('renderTime',request.render.render_time or self._get_render_redis_time())

    def _get_render_redis_time(self):
        render_time = self.server.get(self.render_redis_time_key)
        if render_time and render_time.isdigit():

            return render_time
        logger.info('render redis time not exist,use default render redis time %s'%self.default_render_redis_time)
        return self.default_render_redis_time

class RenderRedisProxy(RenderRedisBase):

    @params_logging
    def __init__(self,redis_conn_config,render_redis_proxys_key):

        super(RenderRedisProxy,self).__init__(redis_conn_config)
        self.render_redis_proxys_key = render_redis_proxys_key


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict('REDIS_CONN_CONFIG',DEFAULT_REDIS_CONN_CONFIG),
                   crawler.settings.get('RENDER_REDIS_PROXYS_KEY',DEFAULT_RENDER_REDIS_PROXYS_KEY),
                    )

    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('proxy',request.render.proxy or self._get_random_render_proxy())

    def _get_random_render_proxy(self):

        render_proxy = self.server.srandmember(self.render_redis_proxys_key)
        if not render_proxy:
            logger.info('redis render proxy not exist or render proxy is null, use null')
            return ''

        return render_proxy
        # http|https|socket://user:passwd@host:port


class RenderRedisUseCookie(RenderRedisBase):

    @params_logging
    def __init__(self,redis_conn_config,render_redis_use_cookie_key,
                 default_render_redis_use_cookie):
        super(RenderRedisUseCookie,self).__init__(redis_conn_config)
        self.render_redis_use_cookie_key = render_redis_use_cookie_key
        self.default_render_redis_use_cookie = str(default_render_redis_use_cookie)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict('REDIS_CONN_CONFIG',DEFAULT_REDIS_CONN_CONFIG),
                   crawler.settings.get('RENDER_REDIS_USE_COOKIE_KEY',DEFAULT_RENDER_REDIS_USE_COOKIE_KEY),
                   crawler.settings.get('DEFAULT_RENDER_REDIS_USE_COOKIE',DEFAULT_RENDER_REDIS_USE_COOKIE),
                    )


    @render
    def process_request(self, request, spider):
        request.formdata.setdefault('useCookie',request.render.use_cookie or self._get_render_redis_use_cookie()
                                    )

    def _get_render_redis_use_cookie(self):
        use_cookie = self.server.get(self.render_redis_use_cookie_key)
        if use_cookie in ['0','1']:
            return use_cookie
        logger.info('use default_render_redis_use_cookie %s'%self.default_render_redis_use_cookie)
        return self.default_render_redis_use_cookie


