// ==UserScript==
// @name          PUP Network Listener
// @description   This will listen to the network requests and report useful info about them
// ==/UserScript==
// Notes:
//   * is a wildcard character
//   .tld is magic that matches all top-level domains (e.g. .com, .co.uk, .us, etc.)

//The PUP Network Listener will listen to the network requests and collects data
//How to use, just run the snippet. To collect the data just access PUPNetworkListener.<function name>
//functions:
//getActiveRequestCount() - returns the number of requests made since the listener was started
//getTotalRequestCount() - resets the count to 0
//requestList() - return an array of all the requests made since the listener was started
//requestEventList() - returns an array of the network request events since the listener was started (includes the requests)
//reset() - resets all the collected data
//
//running from pup:
// start using: "driver.js_snippet("PUPNetworkListener.js")
// later, to get the request count: "int(driver.execute_script("return window.PUPNetworkListener.getCount();"))"

function exists(elem){
  return typeof elem !== 'undefined' && elem !== null ? true : false
}

if (exists(window)
  && window.top === window.self
  && exists(document)
  && exists(document.head))
{

  var script = document.createElement("script")

  function hereDoc(f) {
    return f.toString().
        replace(/^[^\/]+\/\*!?/, '').
        replace(/\*\/[^\/]+$/, '');
  }

  var pupscript = hereDoc(function(){/*!
  window.PUPNetworkListener = (function() {
    'use strict';
    var oldXHR, stateChangeHandler, prop;
    var count = 0;
    var resolved = 0;
    var requestList = [];
    var requestEventList = [];
    var logging  = false;

    oldXHR = window.XMLHttpRequest;

    stateChangeHandler = function (evt) {
      switch (this.readyState) {
        case oldXHR.OPENED:
          count++;
          requestList.push(this);
          requestEventList.push(evt);

          if (logging)
            console.log('Request opened: ', this, evt);

          break;
        case oldXHR.DONE:
          if (requestList.indexOf(this) > -1){
            resolved++;
            if (logging)
              console.log('Request done: ', this, evt);
          }
          break;
      }
    };

    function newXHR() {
      var xhr = new oldXHR();
      xhr.addEventListener('readystatechange', stateChangeHandler);
      return xhr;
    }

    // Copy original states and toString
    for (prop in oldXHR)
      newXHR[prop] = oldXHR[prop];

    window.XMLHttpRequest = newXHR;


    return {
      getTotalRequestCount: function(){
        return count;
      },
      getActiveRequestCount: function(){
        return count - resolved;
      },
      reset: function(){
        count = 0;
        requestList = [];
        requestEventList = [];
      },
      requestList: function(){
        return requestList;
      },
      requestEventList: function(){
        return requestEventList;
      },
      setLogging: function(enable){
        logging = enable;
      }
    }
  })();
  */});

  script.textContent = pupscript;

  document.head.insertBefore(script, document.head.childNodes[0]);
}