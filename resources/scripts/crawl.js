(function(){
  
  
  window.Crawl = function(){
    var self = this;
    
    
    var listeners = {};
    
    var domain,
        options = {},
        key;
    
    
    self.addEventListener = AddEventListener;
    self.removeEventListener = RemoveEventListener;
    self.__events__ = [];
    self.__events__.fire = FireEvent;
    
    self.queue = Queue;
    
    self.getSettings = GetSettings;
    
    
    function AddEventListener(event, funct){
      if(typeof event != 'string' || typeof funct != 'function') return;
      if(self.__events__.indexOf(event) == -1) self.__events__.push(event);
      if(!listeners[event]) listeners[event] = [];
      listeners[event].push(funct);
    }
    function RemoveEventListener(event, funct){
      if(typeof event != 'string' || typeof funct != 'function') return;
      if(self.__events__.indexOf(event) != -1) self.__events__.splice(self.__events__.indexOf(event), 1);
      if(!listeners[event]) return;
      var index = listeners[event].indexOf(funct);
      while(index>-1){
        listeners[event].splice(index, 1);
        index = listeners[event].indexOf(funct);
      }
    }
    function FireEvent(event, data){
      var data = data || {};
      if(!listeners[event]) return true;
      for(var i=0,funct; funct=listeners[event][i++];)
        if(funct(data) === false) return false;
      return true;
    }
    
    function GetSettings(){
      return options;
    }
    
    function Queue(){
      if(!Channel.isConnected()){
        Channel.addEventListener('connect', Queue);
        Channel.connect();
        return;
      }
      Request('/crawl/queue', {
        'channel': {
          'token': Channel.getToken()
        },
        'options': options,
        'domain': domain
      }, OnQueue, {default: RetryRequest});
    }
    function OnQueue(event){
      key = event.crawl.key;
      Channel.listen(key, OnMessage);
      self.__events__.fire('queue');
    }
    
    function OnMessage(event){
      switch(event.type){
        case 'log':
          self.__events__.fire('log', event.message);
        break;
        case 'page':
          self.__events__.fire('page', {url:event.url, content:event.content});
        break;
      }
    }
    
    function RetryRequest(event){
      event.retry();
    }
    
    
    (function Constructor(){
      domain = arguments[0]
      if (typeof domain != 'string') throw 'Crawl Base Url Must Be a String';
      if (!domain.match(/^(http:\/\/|https:\/\/)?([a-zA-Z0-9_]+\.)+[a-zA-Z]{2,4}(\/[a-zA-Z0-9_-]+)*\/?$/)) throw 'Crawl Base Url Doesn\'t Match Url Scheme';
      if (!!arguments[6] && typeof arguments[6] != 'boolean') throw 'Parameter \'mapnakeddomains\' Must Be a Boolean';
      if (!!arguments[7] && typeof arguments[7] != 'boolean') throw 'Parameter \'stripurls\' Must Be a Boolean';
      options = {
        'urlmatch':           arguments[1],  // regex
        'includedsubdomains': arguments[2],  // regex
        'excludedsubdomains': arguments[3],  // regex
        'includedmimetypes':  arguments[4],  // regex
        'excludedmimetypes':  arguments[5],  // regex
        'mapnakeddomains':    arguments[6],  // bool
        'stripurls':          arguments[7]   // bool
      };
    }).apply(self, arguments);
  }
  
  
})();