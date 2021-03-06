const FilterResult = require('./FilterResult');
const Download = require('./Download');
const _ = require('lodash');
const chalk = require('chalk');
const log = console.log;

module.exports = function (searchService, downloadService, options, client) {
  this.download = new Download(downloadService, searchService, options, client);
  this.filterResult = new FilterResult(options.quality);
  this.searchService = searchService;
  this.downloadService = downloadService;
  this.client = client;
  this.timeout = 2000;

  /**
   * Launch search query, then call a callback
   */
  this.search = () => {
    const query = this.searchService.getNextQuery();
    log(chalk.green("Searching for '%s'"), query);
    const searchParam = {
      req: query,
      timeout: this.timeout,
    };
    const afterSearch = (err, res) => this.onSearchFinished(err, res);
    this.client.search(searchParam, afterSearch);
  };

  /**
   * Callback called when the search query get back
   */
  this.onSearchFinished = (err, res) => {
    if (err) {
      return log(chalk.red(err));
    }
    filesByUser = this.filterResult.filter(res);
    this.checkEmptyResult(filesByUser);
    this.showResults(filesByUser);
  };

  /**
   * If the result set is empty and there is no pending searches quit the process.
   * If there is pending searches, launch the next search.
   * If the resultat set is not empty just log success message.
   */
  this.checkEmptyResult = (filesByUser) => {
    if (_.isEmpty(filesByUser)) {
      log(chalk.red('Nothing found'));
      this.searchService.consumeQuery();
      if (this.searchService.allSearchesCompleted()) {
        process.exit(-1);
      }
      this.search();
    } else {
      log(chalk.green('Search finished'));
    }
  };

  /**
   * Display a list of choices that the user can choose from.
   *
   * @param {array} filesByUser
   */
  this.showResults = (filesByUser) => {
    log(chalk.green('Displaying search results'));

    const choices = _.keys(filesByUser);
    log(choices);

    if (choices.length > 0) {
      const bestFile = filesByUser[choices[0]];
      this.processChosenFile(bestFile);
    }
  };

  /**
   * From the user anwser, trigger the download of the folder
   * If there is pending search, launch the next search query
   *
   * @param {array} answers
   */
  this.processChosenFile = (bestFile) => {
    this.searchService.consumeQuery();
    this.download.startDownloads(bestFile);
    if (this.searchService.allSearchesCompleted()) {
      this.downloadService.downloadLogger.flush();
      this.downloadService.everyDownloadCompleted();
    } else {
      this.search();
    }
  };
};
