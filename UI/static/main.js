(function () {

  'use strict';

  angular.module('WordcountApp', [])

  .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {

    $scope.names = {
            therapist01 : "Alex L",
        therapist02 : "Dave",
        therapist03 : "Johanna",
        therapist04 : "Peter",
        therapist05 : "Mariella",
        therapist06 : "Meri",
        therapist07 : "Melissa",
        therapist08 : "Rosemary",
        therapist09 : "Sabrina",
        therapist10 : "Sandra",
        therapist11 : "Stefanie",
        therapist12 : "Teresa",
        therapist13 : "Mary",
        therapist14 : "Kelly-Lee",
        therapist15 : "Lisa",
        therapist16 : "Joanne",
        therapist17 : "Helena",
        therapist18 : "Alex E"

    };

    $scope.dates = {
        Jan2019: '2019-01-31',
        Feb2019: '2019-02-28',
        March2019: '2019-03-31',
        April2019: '2019-04-30',
        May2019: '2019-05-31',
        June2019: '2019-06-30',
        July2019: '2019-07-31',
        August2019: '2019-08-31',
        September2019: '2019-09-30',
        October2019: '2019-10-31',
        November2019: '2019-11-30',
        December2019: '2019-12-31',
        Jan2020: '2020-01-31',
        Feb2020: '2020-02-28',
        March2020: '2020-03-31',
        April2020: '2020-04-30',
        May2020: '2020-05-31',
        June2020: '2020-06-30',
        July2020: '2020-07-31',
        August2020: '2020-08-31',
        September2020: '2020-09-30',
        October2020: '2020-10-31',
        November2020: '2020-11-30',
        December2020: '2020-12-31',

    };

    $scope.invoiceUpdate='not set';
    $scope.getResults = function() {

      $log.log("test");

      // get the URL from the input
      var userName = $scope.url;
      var userDate = $scope.invoice_date

        getAssociateInvoice(userName,userDate);
        getSupervisorInvoice(userName, userDate);

    };
    $scope.createInvoice = function (invoiceid) {
        $log.log("invoiceid:"+invoiceid)

        $http.post('/recreate-invoice/'+invoiceid,'').
        success(function(status, results) {
          $log.log('success')
          $log.log(results);
          // getWordCount(results);
            $scope.invoiceUpdate = 'Successfully updated associate invoice'

        }).
        error(function(error) {
          $log.log(error);
          $scope.invoiceUpdate = 'Failure in updating associate invoice'
        });
    };
    $scope.upload = function () {
        $log.log("upload")

        $http.post('/uploaded','').
        success(function(status, results) {
          $log.log('success')
          $log.log(results);
          // getWordCount(results);
            $scope.invoiceUpdate = 'Successfully updated file'

        }).
        error(function(error) {
          $log.log(error);
          $scope.invoiceUpdate = 'Failure in updating file'
        });
    };
    $scope.persistInvoice = function() {

        var st = $scope.wordcounts[0].status;
        $log.log("test3455"+st);

        var allInvoices = [];
        for (var i=0; i < $scope.wordcounts.length; i++) {
            //$log.log($scope.wordcounts[i]);
              var eachInvoice =
                     {
                         "name": $scope.wordcounts[i].name,
                         "id": $scope.wordcounts[i].id,
                         "tax":$scope.wordcounts[i].tax,
                         "subtotal":$scope.wordcounts[i].subtotal,
                         "total":$scope.wordcounts[i].total
                     };
               allInvoices.push(eachInvoice);

        }

        $log.log(allInvoices);
        /*$http.post('/update-invoice', allInvoices).
        success(function(status, results) {
          $log.log('sucess')
          $log.log(results);
          // getWordCount(results);
            $scope.invoiceUpdate = 'Successfully updated associate invoices'

        }).
        error(function(error) {
          $log.log(error);
          $scope.invoiceUpdate = 'Failure in updating associate invoices'
        });*/
    };


    function getAssociateInvoice(userInput,userDate) {

      var timeout = "";
      $scope.invoiceUpdate = "";
      var poller = function() {
        // fire another request
        $http.get('/results/'+userInput+'/'+userDate).
          success(function(data, status, headers, config) {
            if(status === 202) {
              //$log.log(data, status);
            } else if (status === 200){
              $log.log(data);
              $scope.wordcounts = data;
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 2000);
          });
      };
      poller();
    };

    function getSupervisorInvoice(userInput,userDate) {

      var timeout = "";
      $scope.invoiceUpdate = "";

      var poller = function() {
        // fire another request
        $http.get('/supervisor-results/'+userInput+'/'+userDate).
          success(function(data, status, headers, config) {
            if(status === 202) {
              //$log.log(data, status);
            } else if (status === 200){
              $log.log(data);
              $scope.supervisorCounts = data;
              $timeout.cancel(timeout);
              return false;
            }
            // continue to call the poller() function every 2 seconds
            // until the timeout is cancelled
            timeout = $timeout(poller, 2000);
          });
      };
      poller();
    }

  }
  ]);

}());

