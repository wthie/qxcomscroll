//qxathena.js - a minimal Qooxdoo - Athena merge
//
//author   : Werner Thie, wth
//last edit: wth, 26.08.2015
//modhistory:
//  26.02.2010 - wth, smooth and easy programming so far
//  24.03.2010 - wth, successful integration of qooxdoo & nevow
//  17.05.2010 - wth, fiddled with the imports quite a bit
//  23.05.2010 - wth, added some very primitive testing code
//  27.01.2011 - wth, set transparency to let wb's background work shine
//                    without blinking
//  04.02.2011 - wth, signals production run back to client counterpart, thus 
//                    reducing logging on the client
//  24.02.2011 - wth, image rebasing code fixed a key error
//  07.02.2013 - wth, inserting img into DOM after initial load is of no help 
//                    at all with mobile Safari
//  19.06.2015 - wth, another go at a tighter nevow/qooxdoo integration brought relieve
//  17.08.2015 - wth, slight optimisation, no need for nevow node to detect itself

// import Nevow.Athena

qxcomscroll.common.helpers.Widget.subclass(qxcomscroll.qxathena.qxathena, 'QxAthena').methods(
  function __init__(self, node) {
    qxcomscroll.qxathena.qxathena.QxAthena.upcall(self, '__init__', node);
  },

  function initQooxdoo(self) {
    var dt = 0.2;
    
    function startup(parms) {
      var code = parms[0];          //determination between production and test run
      var relocateImgs = parms[1];
      
      self.attachWidget(self.inlineIsle.getContentElement().getDomElement(), 'QxPlayground', []);
      if (code) {
        Divmod.log('qxathena', 'PRODUCTION run detected - removing all log observers...');
        Divmod.logger.observers = [];
      } else {
        Divmod.log('qxathena', 'TEST run detected - keep log observers intact...');

        //support additional cross-browser console
        qx.log.appender.Console.show();
      }
      //quite a hefty incision into qooxdoo basics; see the relevant code in qx/util/ResourceManager.js
      //which provides a single path situation for finding resources like images on other servers, thus
      //relieving our humble servers from the static file delivery part
      for (var lib in relocateImgs) {
        qx.$$libraries[lib].resourceUri = relocateImgs[lib];
      }

// this code is a complete waste, mobile Safari does NOT load images inserted into the DOM in this way      
//      var img = qx.dom.Element.create("img");
//      qx.bom.element.Attribute.set(img, "src", "resource/qxathena/images/error.png");
//      qx.bom.element.Class.add(img, "hide");
//
//      qx.dom.Element.insertAfter(img, self.nodeById('qooxdoo-root'));
    }

    // waitforQooxdoo - waits until the qooxdoo part has booted up on the browser, the flag
    // window.qx.AppLoaded will be visible and True if this has happened. A qooxdoo inline root
    // is created as child of the nevow node After that a remote call to the server
    // to the server is triggered, signaling this aspect, with the return from the server the nevow
    // widget QxPlayground is instantiated and attached. This operation concludes the setting up of
    // the whole nevow/qooxdoo mixup. QxPlayground is usually the place then, where lots of qooxdoo
    // objects are aggregated together constituting whatever application
    function waitforQooxdoo() {
      if (window.qx.AppLoaded) {
        self.inlineIsle = globals.inlineIsle = new qx.ui.root.Inline(self.node, true, true).set({
          backgroundColor: 'transparent'
        });
        self.inlineIsle.setLayout(new qx.ui.layout.Canvas()); //QxPlayground's container will be resized to the inlineIsle's size if
                                                              //added with globals.inlineIsle.add(self.container, { edge: 0});
        var d = self.callRemote('initQooxdoo', 'dummy');
        d.addCallback(startup);
      }
      else {
        self.callLater(dt, waitforQooxdoo);
      }
    }

    self.callLater(dt, waitforQooxdoo);
  },

  // attachWidget - slightly modified version, allowing to specify the parent node of the
  //                widget to be attached. This feature allows for proper DOM setup, in the
  //                first implementations the irritating problem was, that CSS could not be
  //                used properly because of parent/child relationsship being off

  // self         - explanatory
  // node         - the DOM node to attach the widget to, this is necessary to be able to
  //                attach the nevow items to the qooxdoo island
  // name         - Python function called remotely creating a nevow Live Fragment
  // params       - parameters passed down to function above
  // readyfunc    - the function called after the the ready function of the widget has
  //                done its work, standard callback func, errback is handled in attachWidget
  // readyparams  - wrong place, should come before readyfunc, is params to the widget's ready
  //                function, which produces the deferred then calling readyfunc, will try to
  //                have these two guys exchange places
  function attachWidget(self, node, name, params, readyfunc, readyparams) {
    var d1 = self.callRemote(name, params);
    d1.addCallback(function liveElementReceived(le) {
      Divmod.debug('liveElementReceived', 'liveElementReceived: ' + name);
      var d2 = self.addChildWidgetFromWidgetInfo(le);
      d2.addCallback(function childAdded(widget) {
        if (node) {
          node.appendChild(widget.node);
        } else {
          self.node.appendChild(widget.node);
        }
        var d3 = widget.ready(readyparams);
        function isready(res, widget) {
          widget.show();
        }
        if (!readyfunc)
          readyfunc = isready;
        d3.addCallback(readyfunc, widget);
        d3.addErrback(function(res) {
          self.genericErrback(name, 'readyfunc', res);
        });
      });
      d2.addErrback(function(res) {
        self.genericErrback(name, 'childAdded', res);
      });
    });
    d1.addErrback(function(res) {
      self.genericErrback(name, 'liveElementReceived', res);
    });
  },

  function ready(self) {
    var d = loadImages([]);
    return d;
  },

  function show(self) {
    self.node.style.visibility = 'visible';
    self.initQooxdoo();
  }
);
