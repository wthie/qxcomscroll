//qxplayground.js - the minimal Qooxdoo playground
//
//author   : Werner Thie, wth
//last edit: wth, 27.08.2015
//modhistory:
//  21.03.2011 - wth, added clock functionality right here instead of adding another widget
//  19.07.2011 - wth, connection lost dialog now properly shown
//  19.11.2011 - wth, moved forward to V1.5 of qooxdoo
//  07.02.2013 - wth, diddled with img preloading again for mobile Safari, logging in qooxdoo
//  27.08.2015 - wth, revamped with the new minimized widget attachment

// import Nevow.Athena
// import qxcomscroll.common.globals
// import qxcomscroll.common.helpers

qxcomscroll.common.helpers.Widget.subclass(qxcomscroll.qxathena.qxplayground, 'QxPlayground').methods(
  function __init__(self, node) {
    qxcomscroll.qxathena.qxplayground.QxPlayground.upcall(self, '__init__', node);
    var layout = new qx.ui.layout.Grow();
    self.container = new qx.ui.container.Composite(layout).set({
      //backgroundColor: 'yellow'      
    });
    globals.inlineIsle.add(self.container, { edge: 0});
    self.autoscroll = true;
    self.prevlog = [];
  },

  function init(self) {
    if (globals.reqType == REQ_ROOT) {
      var body = new qx.ui.container.Composite(new qx.ui.layout.Dock()).set({
      });
      
      var scroller = new qx.ui.container.Scroll().set({
        decorator: 'main',
        backgroundColor: '#f2f2f2',
        opacity: 0.75,
        paddingLeft: 5
      });
      
      scroller.getChildControl('scrollbar-y').addListener('scroll', function(e) {
        var pane = scroller.getChildControl('pane');
        var paneSize = pane.getInnerSize();
        var scrollSize = pane.getScrollSize();
      
        self.autoscroll = (scroller.getScrollY() == scrollSize.height - paneSize.height);
        if (self.autoscroll) {
          self.pending = 0;
        }
      });
    
      var log = new qx.ui.basic.Label().set({
        textColor: 'black',
        font : new qx.bom.Font(28, ["Verdana", "sans-serif"]),
        rich: true
      });
      self.log = log.toHashCode();
      scroller.add(log);
      self.scroller = scroller.toHashCode();
      body.add(scroller, {edge: 'north', flex: 1});
      
      var buttons = new qx.ui.container.Composite(new qx.ui.layout.HBox(8).set({
        alignX : "left"
      }));
    
      var stBtn = new qx.ui.form.Button('Start/Stop').set({
        height:40,
        width: 200
      });
      stBtn.addListener('execute', function(e) {
        var d = self.callRemote('toggleBeat');
      });
      buttons.add(stBtn);
    
      var resetBtn = new qx.ui.form.Button('Reset').set({
        height:40,
        width: 200
      });
      resetBtn.addListener('execute', function(e) {
        var d = self.callRemote('resetAll');
      });
      buttons.add(resetBtn);
    
      body.add(buttons, {edge: 'south'});
      self.container.add(body);
    }
    else {
      alert('Unknown Request Type: ' + globals.reqType);
      //self.attachWidget('fourOfour', 404);
    }
  },
  
  function append(self, id, msg) {
    var log = fromHashCode(self.log);
    var scroller = fromHashCode(self.scroller);
    
    self.prevlog.push('<i>' + id + ': </i>' + msg);
  
    if (self.prevlog.length > 256) {
      self.prevlog.splice(0, 1);
    }
  
    log.setValue(self.prevlog.join('<br/>'));
  
    if (self.autoscroll) {
      scroller.scrollToY(99999, 0);
    } else {
      if (scroller.getChildControl('scrollbar-y').isVisible()) {
        self.pending += 1;
      }
    }
  },
  
  function beat(self, id, msg) {
    self.append(id, msg); 
  },

  function reset(self) {
    var log = fromHashCode(self.log);
    self.prevlog = []; 
    log.setValue('');
  },

  function show(self, pcode) {
    self.node.style.visibility = 'visible';
    self.init();
  }
);
