
__version__ = "0.1"
__all__ = ["DTpod_service"]
__author__ = "bones7456"
__home_page__ = "http://li2z.cn/"
from DTsubscription_oracle import DTsubscription_oracle
import os
from DTauthenticator import DTauthenticator
import posixpath
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
import cgi
import json
import base64
from DTutilities import get_obligation_by_res_path
from DTaddresses import *

import mimetypes
try:
    from io import StringIO
except ImportError:
    from io import StringIO
"""
Class that implements the pod's web service.
The class allows the pod to deliver on demand data through the HTTP protocol
"""
class DTpod_service(BaseHTTPRequestHandler):
                
    server_version = "SimpleHTTPWithUpload/" + __version__
    authenticator=DTauthenticator()
    """
    Initializer of the class
    """
    def __init__(self, pod_pk,*args):
        self.pod_pk=pod_pk
        self.subscription_oracle=DTsubscription_oracle(DTSUBSCRIPTION,self.pod_pk)
        BaseHTTPRequestHandler.__init__(self, *args)

    """
    Handling of GET requests. 
    Can only be internally invoked by the do_POST() function.
    Deliver the resource in the HTTP response.
    """
    def do_GET(self,auth_token=None,claim=None,id_subscription=None):
        print(auth_token,claim,id_subscription,self.path)
        if auth_token==claim==id_subscription==None:
            self.send_error(400, "Bad request, Credentails missing")
            return None
        if not self.authenticator.authenticate(self.path,auth_token,claim):
            self.send_error(400, "Authentication failed, Check your credentails and internet connection")
            return None
        self.usage_policy = get_obligation_by_res_path(self.path)
        authorized_country = self.usage_policy['country']
        if authorized_country['value'] != "Unrestricted" :
            auth_check = self.authenticator.authenticate_country_with_ip(authorized_country)
            if(auth_check is None):
                self.send_error(400, "Authentication failed, Check your internet connection.")
                return None
            if not auth_check:
                self.send_error(400, "Authentication failed, Unauthorized country obligation")
                return None
            # if not self.subscription_oracle.pull_subscription_verification(int(id_subscription),claim):
            #     self.send_error(400, "Subscription not verified, bad request")
            #     return None
        f = self.send_head()     
        result= f if f is not None else None
        if f:
            if type(result)==type("a"):
                self.wfile.write(bytes(result,'utf-8'))
            else:
                self.wfile.write(result)
            # f.close()
    """
    Handling of POST requests. 
    After the extraction of the POST body parameters from the request, it invokes the do_GET() function.
    """  
    def do_POST(self):
        claim=None
        auth_token=None
        try:
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        except Exception:
            self.send_error(400,"Bad Request")
        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = self.headers.get('content-length')
            fields = cgi.parse_multipart(self.rfile, pdict)
            try:
                if(fields.get("auth_token") == None or fields.get("id_subscription") == None  or fields.get("claim") == None ):
                    self.send_error(400,"Bad Request. Credentials missing")
                auth_token = fields.get('auth_token')[0]
                claim=fields.get("claim")[0]
                id_subscrption=fields.get("id_subscription")[0]
            except Exception as e:
                auth_token=None
                claim=None
                print (e)
        self.do_GET(auth_token,claim,id_subscrption)
    """
    Sets the head of the HTTP response.
    """ 
    def send_head(self):
        path = self.translate_path(self.path)
        result = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            else:
                self.send_error(404,"Pod resource not found")
        ctype = self.guess_type(path)
        result = {
        "usage_policy": self.usage_policy,
        }
        try:
            with open(path, "rb") as file:
                file_content = file.read()
            file_name_full = path.split('/')[-1]
            file_name = file_name_full.split('.')[0]
            extn = file_name_full.split('.')[1]
            result["resource"] = { 
                "file_name":file_name,
                "extension":extn,
                "file_name_full": file_name_full,
                "base64_encoded_image" : base64.b64encode(file_content).decode('utf-8'),
                }
            result = json.dumps(result)
        except IOError:
            self.send_error(404, "Pod resource not found")
            return None
        self.send_response(200)
        self.send_header("Content-type",'application/json') #ctype
        self.end_headers()
        return result
    
    """
    Standardizes the URL path pointing to the requested resource.
    """     
    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        return self.server.base_path +"/"+ words[2]+'/'+words[3] # remove '/'+words[3] if /images is removed
    """
    Defines the type of the requested resource.
    """ 
    def guess_type(self, path):

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

"""
Wrapper class used to create Stoppable instances of HTTP servers.
"""      
class StoppableHTTPServer(HTTPServer):

    stopped = True
    allow_reuse_address = True
    """
    Class initializer.
    """  
    def __init__(self, *args, **kw):
        HTTPServer.__init__(self, *args, **kw)
        self.base_path=args[2]

    """
    Puts the server on listening of HTTP requests.
    """
    def serve_forever(self):
        try:
            while self.stopped:
                self.handle_request()
        except Exception as e:
            print()       
    """
    Stops the requests listening.
    """
    def force_stop(self):
        print("Stopping server...")
        self.stopped = True
        # self.server_close()


