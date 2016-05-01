//mainpage.js - dummy mainpage module for preloading the JS code
//
//author   : Werner Thie, wth
//last edit: wth, 26.08.2015
//modhistory:
//  20.01.2011 - wth, pruned for minimal

// import Divmod
// import Nevow.Athena

Nevow.Athena.PageWidget.subclass(qxcomscroll.web.mainpage, 'Mainpage').methods(
  function _TStr(self, id) {
    try {
      return globals.texts[id];   //whatever must remain global for texts
    }
    catch(err) {
      return id + ': undefined';
    }
  },

  function showDisconnectDialog(self) {
    var c = new qx.ui.container.Composite();      //transparent centering container
    globals.inlineIsle.add(c, {edge: 0});

    var l = new qx.ui.layout.HBox();
    c.setLayout(l);
    l.setAlignX("center");
    l.setAlignY("middle");

    var errorDlg = new qx.ui.container.Composite().set({
      backgroundColor: '#c2c2c2',
      padding: 16
    });
    errorDlg.setLayout(new qx.ui.layout.VBox(10));
    errorDlg.setAllowGrowY(false);
    c.add(errorDlg);

    var warn1 = new qx.ui.basic.Atom(self._TStr('discoError'), 'qxathena/images/error.png').set({rich: true, maxWidth: 550, minWidth: 550});
    errorDlg.add(warn1);

    Divmod.msg("Connection lost, dialog being shown now!");
  }
);
