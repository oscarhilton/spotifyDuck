const chalk = require('chalk');
const slsk = require('slsk-client');
const Search = require('../modules/Search');
const SearchService = require('../services/SearchService');
const DownloadService = require('../services/DownloadService');
const { promises } = require('fs');
const log = console.log;

class SoulseekCli {
  constructor(username, password, toDownload, destination) {
    this.username = username;
    this.password = password;
    this.connected = false;

    this.toDownload = toDownload;
    this.destination = destination;

    this.searchService = new SearchService(toDownload);
    this.downloadService = new DownloadService(this.searchService);
    
    this.search = null;

    this.connect();
  }

  /**
   * Connect to the Soulseek client
   */
  connect() {
    if(!this.username || !this.password) {
      return;
    }
    slsk.connect({
      user: this.username,
      pass: this.password,
    }, (err, client) => this.onConnected(err, client));
  }

  /**
   * @param  {string}
   * @param  {SlskClient}
   */
  onConnected(err, client) {
    if (err) {
      return log(chalk.red(err));
    };

    this.connected = true;
    log(chalk.green('Connected to soulseek'));
    this.makeDownloadLoop(client);
  };

  async makeDownloadLoop(client) {
    this.search = null;
    this.search = new Search(this.searchService, this.downloadService, {
      destination: this.destination,
      quality: 320,
    }, client);
    this.search.search();
  }
}

module.exports = SoulseekCli;
