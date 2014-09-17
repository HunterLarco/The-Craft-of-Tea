// requires google app engine channel jsapi
// requires my Request.js file

(function(){
  
  // events
  // onopen
  //  ~ when the channel is opened in the browser
  // onerror
  // onclose
  // onconnect
  //  ~ when the channel recieves a connection verification ping from the server
  
  window.Channel = new (function(){
    var self = this;
    
    
    var tokens = {client:null},
        channel;
    
    var listeners = {};
    
    var messagelisteners = {};
    
    var isConnected = false;
    
    
    self.addEventListener = AddEventListener;
    self.removeEventListener = RemoveEventListener;
    self.__events__ = [];
    self.__events__.fire = FireEvent;
    
    self.connect = Connect;
    self.listen = Listen;
    
    self.getToken = GetToken;
    self.isConnected = IsConnected;
    
    
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
    
    function GetToken(){
      return tokens.client;
    }
    function IsConnected(){
      return isConnected;
    }
    
    function Listen(freq, funct){
      if(typeof funct != 'function') throw 'Expected Function';
      if(!messagelisteners[freq]) messagelisteners[freq] = [];
      messagelisteners[freq].push(funct);
    }
    function FireMessageListener(freq, message){
      if(!messagelisteners[freq]) return;
      for(var i=0,listener; listener=messagelisteners[freq][i++];)
        listener(message);
    }
    
    function OnError(){
      console.warn('Channel Error');
      self.__events__.fire('error');
    }
    function OnClose(){
      console.warn('Channel Closed');
      self.__events__.fire('close');
    }
    
    function Connect(){
      Request('/channel/connect', {}, function Callback(event){
        Open(event.tokens.client);
      }, {default:RetryRequest});
    }
    function Open(clienttoken){
      tokens.client = clienttoken;
      
      channel = new goog.appengine.Channel(clienttoken);
      
      channel = channel.open({
        'onopen': OnOpen,
        'onmessage': OnMessage,
        'onerror': OnError,
        'onclose': OnClose
      });
    }
    function OnOpen(){
      self.__events__.fire('open', self);
      VerifyConnection();
    }
    function VerifyConnection(){
      var hasRecievedPing = false,
          retryTime = 0,
          pingInterval = null;
      
      Listen('ping', PingRecieved);
      function PingRecieved(){
        if(hasRecievedPing) return;
        clearTimeout(pingInterval);
        hasRecievedPing = true;
        OnVerified();
      }
      
      function Ping(){
        Request('/channel/ping', {
          'token': tokens.client
        }, null, {default:new Function()});
      
        var seconds = Math.pow(2, ++retryTime);
        
        if(pingInterval != null)
          console.log('Ping Not Recieved... Retrying Channel Ping in '+seconds+' Seconds');
        
        pingInterval = setTimeout(Ping, seconds*1000);
      }
      
      Ping();
    }
    function OnVerified(){
      isConnected = true;
      self.__events__.fire('connect', self);
    }
    
    function OnMessage(event){
      var event = JSON.parse(event.data),
          freq = event.frequency,
          data = event.message;
      FireMessageListener(freq, data);
    }
    
    function RetryRequest(event){
      event.retry();
    }
    
  })();
  
})();