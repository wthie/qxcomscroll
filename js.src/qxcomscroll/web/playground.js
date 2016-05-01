//playground.js - let's users play whatever games, contains the whole startup
//                logic for the site. This is the client side part of the basis
//                of this whole web site. If you plan for yet another sequencing of
//                events on startup then please change the code here. The actual
//                implementation starts, waits for all images to be loaded (assuming
//                that all images are loaded before user interaction is allowed.
//                That's why there is a waitroller shown during image loading and after
//                all is set and done a READY message is displayed.
//
//author   : Werner Thie, wth
//last edit: wth, 07.02.2013
//modhistory:
//  20.01.2011 - wth, pruned for minimal
//  07.02.2013 - wth, improved the rsrc checking code sligthly
 
// import Nevow.Athena
// import qxcomscroll.common.globals
// import qxcomscroll.common.helpers

//this is just another basic widget derived from common.helpers.Widget with a twist
//insofar, as the insertion happens through the basic insertion method within the 
//delivered pages html, namely <nevow:invisible nevow:render="playground" /> which
//pumps up a standard lifepage with exactly one fragment inserted. After initialization
//Divmod.Runtime.theRuntime. issues a call via the preset vector which contains 
//globals.playground.appStartup you'll find below. This call then starts the pulling in
//of whatever is needed, please see additional comments below

qxcomscroll.common.helpers.Widget.subclass(qxcomscroll.web.playground, 'Playground').methods(
  function __init__(self, node) {
    qxcomscroll.web.playground.Playground.upcall(self, '__init__', node);
    globals.playground = self; //this is the crucial ref for the startup sequence.
                               //If problems during startup are observed then please
                               //have a look at this code
  },

  function showWaitRoller(self){  
    var waitroller = self.nodeById('waitroller');
    waitroller.style.visibility = 'visible';
  },
  
  function hideWaitRoller(self) {
    var waitroller = self.nodeById('waitroller');
    waitroller.style.visibility = 'hidden';
  },

  //do whatever needs to be started up, checking for images loading
  //and other gory stuff. This function is called by the Divmod.Runtime
  //code as startup event, see globals.js
  //
  //---- initialization sequence to be followed
  //  mainpage.py/.js       - the LivePage with the task of keeping up the nevow/athena RPC system
  //  playground.py/.js     - the mother of all widgets which gets the startup call in the beginning
  //                          then attaching whatever you please to attach to it.
  //                          A perfectly working version with qooxdoo is available as well as some
  //                          trials with processing for mobile webapps. This would also be the place
  //                          to decide on platform specific issues, like delivering qooxdoo to the
  //                          desktop vs processing to the mobile client using HTML5 to its full extent
  
  function appStartup(self) {
    function ready() {                                        //we're now ready for action
      var d1 = self.callRemote('guiready');
      
      d1.addCallback(function(res){ 
        globals.__init__();
        globals.reqType = res[0];
        globals.user    = res[1];
        self.hideWaitRoller();                //seems we're done, hide the visual amusements for now
        qx.log.Logger.debug('appStartup -' );     
        self.attachWidget('QxAthena', []);    //don't need the params in this case
      });
    
      d1.addErrback(function(res) {
        self.node.appendChild(document.createTextNode('Error: ' + res.error.message));
      });
    }
    
    function checkRsrcLoading() {
      //this is temporarily switched off until we decide how the CSS should look like
      //the testing CSS contains a lot of unavailable URIs for images which is sending us
      //into neverland when trying to load them. The current notion seems to be to have
      //only one big image and cutting out bits of it with CSS functionality which works
      //quite well once you've mastered the trick
      //   
      //var uris = [];                  //case of manually adding images
      //uris.push('http://80.86.202.40/jgame.png');
      //or
      //var uris = collectCSS_backgroundImages(['http://80.86.202.40/xxx.png', 'http://80.86.202.40/yyy.png']);
      //var uris = collectCSS_backgroundImages([], collectClasses(self.node));
      //var uris = collectCSS_backgroundImages([], null); //collect ALL images in CSS everywhere
      var uris = [];
      uris[uris.length] = qx.util.ResourceManager.getInstance().toUri('qxathena/images/error.png');
      var di = loadImages(uris);       
      var dt = self.callRemote('getTexts', ['discoError']);
      dt.addCallback(function(texts) {
        globals.texts = texts;  //could use concat'ing whatever comes back
      }); 
      var dlist = new Divmod.Defer.DeferredList([di, dt], false /*fireOnOneCallback*/, false /*fireOnOneErrback*/, true /*consumeErrors*/);
      dlist.addCallback(ready);
      dlist.addErrback(function(res) {
        alert(res.error.message);
      });
    }

    checkRsrcLoading();
  }
);
