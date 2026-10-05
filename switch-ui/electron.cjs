const { app, BrowserWindow } = require("electron");

let win;

let backendWasConnected = false;
let backendMissingSince = null;


function createWindow() {

  win = new BrowserWindow({

    width: 300,
    height: 300,

    minWidth: 180,
    minHeight: 180,

    maxWidth: 600,
    maxHeight: 600,

    frame: false,

    transparent: true,

    backgroundColor: "#00000000",

    hasShadow: false,

    resizable: true,

    movable: true,

    minimizable: false,

    maximizable: false,

    alwaysOnTop: true,

    skipTaskbar: true,

    show: false,

    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });


  win.setBackgroundColor(
    "#00000000"
  );


  win.loadURL(
    "http://localhost:5173"
  );


  win.setAlwaysOnTop(
    true,
    "floating"
  );


  win.once(
    "ready-to-show",
    () => {
      win.show();
    }
  );


  // Keep SWITCH above normal windows.
  win.on("blur", () => {

    if (
      win &&
      !win.isDestroyed()
    ) {

      win.setAlwaysOnTop(
        true,
        "floating"
      );
    }
  });


  // Watch Python backend.
  const stateInterval =
    setInterval(
      async () => {

        if (
          !win ||
          win.isDestroyed()
        ) {

          clearInterval(
            stateInterval
          );

          return;
        }


        try {

          const response =
            await fetch(
              "http://127.0.0.1:5000/state",
              {
                cache: "no-store"
              }
            );


          const data =
            await response.json();


          backendWasConnected =
            true;

          backendMissingSince =
            null;


          if (
            data.state ===
            "exiting"
          ) {

            clearInterval(
              stateInterval
            );


            setTimeout(() => {

              if (
                win &&
                !win.isDestroyed()
              ) {

                win.close();
              }

            }, 2500);
          }

        } catch {

          // Backend disappeared.
          // This happens when main.py exits.

          if (backendWasConnected) {

            if (
              backendMissingSince ===
              null
            ) {

              backendMissingSince =
                Date.now();
            }


            // Give the backend a short
            // grace period, then close UI.

            if (
              Date.now() -
              backendMissingSince >
              1000
            ) {

              clearInterval(
                stateInterval
              );


              if (
                win &&
                !win.isDestroyed()
              ) {

                win.close();
              }
            }
          }
        }

      },
      100
    );
}


app.whenReady().then(
  createWindow
);


app.on(
  "window-all-closed",
  () => {
    app.quit();
  }
);