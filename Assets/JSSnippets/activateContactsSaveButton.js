function fireEvent(obj, evt){
     var fireOnThis = obj;
     if( document.createEvent ) {
       var evObj = document.createEvent('MouseEvents');
       evObj.initEvent( evt, true, false );
       fireOnThis.dispatchEvent( evObj );
       console.log('check abc')
     }
      else if( document.createEventObject ) { //IE
       var evObj = document.createEventObject();
       fireOnThis.fireEvent( 'on' + evt, evObj );
     }
}
tr = document.getElementsByClassName("simple-table")[0].getElementsByTagName("td")[0];
tds = tr.getElementsByClassName("ng-scope ng-isolate-scope");

for(kiter = 0; kiter < tds.length; kiter++){
    j=kiter;
    console.log("starting " + j);
    fireEvent(tds[j],"change");
    console.log(j + " is done");
}