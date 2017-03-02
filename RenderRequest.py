#coding=utf-8
import scrapy
from six.moves.urllib.parse import urljoin, urlencode
from scrapy.utils.python import to_bytes, is_listlike


def _urlencode(seq, enc):
    values = [(to_bytes(k, enc), to_bytes(v, enc))
              for k, vs in seq
              for v in (vs if is_listlike(vs) else [vs])]
    return urlencode(values, doseq=1)


class Render(object):
    def __init__(self,render_url=None,render_time='',proxy=None,use_cookie=0,content_type='html',
                 script='',user_agent=None):
        self.render_url = render_url
        self.render_time = str(render_time)
        self.proxy = proxy
        self.use_cookie = str(use_cookie)
        self.content_type = content_type
        self.script = script
        self.user_agent = user_agent


class RenderRequest(scrapy.Request):
    def __init__(self,*args,**kwargs):
        self.render = kwargs.pop('render',Render())
        self.formdata = kwargs.get('formdata',{})
        self.params = kwargs.pop('params',None)

        super(RenderRequest, self).__init__(*args, **kwargs)
        self.method = 'POST'
        if self.params:
            items = self.params.items() if isinstance(self.params, dict) else self.params
            querystr = _urlencode(items, self.encoding)
            self._set_url(self.url + ('&' if '?' in self.url else '?') + querystr)

