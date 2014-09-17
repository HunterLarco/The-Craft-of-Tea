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
      self.__events__.fire('queue');
    }
    
    function RetryRequest(event){
      event.retry();
    }
    
    
    (function Constructor(){
      domain = arguments[0]
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