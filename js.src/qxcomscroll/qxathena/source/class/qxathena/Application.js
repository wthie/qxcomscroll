/* ************************************************************************

   Copyright:

   License:

   Authors:

************************************************************************ */

/* this Application.js file was created with
  
./qooxdoo/qooxdoo-5.0.1-sdk/tool/bin/create-application.py -n qxathena -t inline

************************************************************************

#asset(qxathena/*)

#use(qx.log.appender.Console)  

#use(qx.ui.root.Inline)

#use(qx.ui.layout.VBox)
#use(qx.ui.layout.HBox)
#use(qx.ui.layout.Canvas)
#use(qx.ui.layout.Grid)
#use(qx.ui.layout.Dock)

#use(qx.ui.groupbox.GroupBox)

#use(qx.ui.form.Button)
#use(qx.ui.form.TextField)
#use(qx.ui.form.PasswordField)
#use(qx.ui.form.SelectBox)
#use(qx.ui.form.ListItem)
#use(qx.ui.form.Slider)

#use(qx.ui.embed.Html)
#use(qx.ui.embed.Iframe)
#use(qx.html.Canvas)
#use(qx.html.Image)

#use(qx.ui.container.Scroll)

/************************************************************************ */

/**
 * This is the main application class of your custom application "qxathena"
 */
qx.Class.define("qxathena.Application",
{
  extend : qx.application.Inline,



  /*
  *****************************************************************************
     MEMBERS
  *****************************************************************************
  */

  members :
  {
    /**
     * This method contains the initial application code and gets called 
     * during startup of the application
     * 
     * @lint ignoreDeprecated(alert)
     */
    main : function()
    {
      // Call super class
      this.base(arguments);

      // Enable logging in debug variant
      if (qx.core.Environment.get("qx.debug"))
      {
        // support native logging capabilities, e.g. Firebug for Firefox
        qx.log.appender.Native;
        // support additional cross-browser console. Press F7 to toggle visibility
        qx.log.appender.Console;
      }

      if (!window.qx) {                                   // nevow/athena main connection points
        window.qx = qx;
      }

      window.qx.AppLoaded = true;
    }
  }
});
