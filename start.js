var Client = require("socket.engine").client;

const HOST = "127.0.0.1";
const PORT = "9999";

var c = new Client(addr=HOST, port=PORT);
c.start();

c.on("Test", (data) => {
  console.log(data);
});

c.write("Test", "Hello there!");
c.get("Test");


// const Hub = require("socket.engine").Hub;
// const fs = require('fs');
// const SoulseekCli = require('./commands/soulseek-cli');
// var randomWords = require('random-words');

// console.log("STARTING HUB")

// const COMMANDS = {
//   PING: 'PING',
//   DOWNLOAD_MISSING: "DOWNLOAD_MISSNIG",
// };

// const h = new Hub(9999);

// h.connect("hello!", "127.0.0.1", 8080);


// h.on(COMMANDS.PING, (data) => {
//   console.log(data);
// })

// h.on(COMMANDS.DOWNLOAD_MISSING, (data) => {
//   console.log(data);
//   const CONFIG_TXT = 'config.txt';
//   const NOT_DOWNLOAD_FILES_TXT = 'not_download.txt';

//   fs.readFile(CONFIG_TXT, 'utf8' , (err, data) => {
//     if (err) {
//       console.error(err)
//       return
//     }

//     const { username, password, location } = JSON.parse(data);

//     fs.readFile(NOT_DOWNLOAD_FILES_TXT, 'utf8' , async (err, data) => {
//       if (err) {
//         console.error(err)
//         return
//       }
    
//       const filesToDownload = JSON.parse(data);
    
//       let downloadList = [];
//       for (const file of filesToDownload) {
//         const { Album, Track, Artists } = file;
//         const searchForThis = (Album === Track) ? Track + ' ' + Artists  : Album ? Album + ' ' + Track + ' ' + Artists : Track;
//         downloadList.push(searchForThis);
//       }

//       return new SoulseekCli(randomWords({ exactly: 3, join: ' ' }), randomWords({ exactly: 3, join: ' ' }), downloadList, location);
//     });
//     return;
//   });

//   h.close();
// });

// console.log(h)

// h.write_to_local(COMMANDS.PING, "HELLO")