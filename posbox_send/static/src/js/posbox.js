odoo.define('posbox_send.posbox', function (require) {

    var Session = require('web.Session');

    var posbox = function () {
        this.connect = null;
        this.connection = null;
        this._status = {};
        this.notifications = {};
        this.keptalive = false;
        this.receipt_queue = [];

        this.connect = function (url) {
            var self = this;
            this.connection = new Session(undefined, url, {use_cors: true});
            this.host = url;
            this.set_connection_status('connecting', {});

            return this.message('handshake').then(function (response) {
                if (response) {
                    console.error('Connection connected');
                    self.set_connection_status('connected');
                    localStorage.hw_proxy_url = url;
                    self.keepalive();
                } else {
                    self.set_connection_status('disconnected');
                    console.error('Connection refused by the Proxy');
                }
            }, function () {
                self.set_connection_status('disconnected');
                console.error('Could not connect to the Proxy');
            })
        }

        this.status = function () {
            var self = this;
            self.connection.rpc('/hw_proxy/status_json', {}, {timeout: 2500})
                .then(function (driver_status) {
                    self.set_connection_status('connected', driver_status);
                }, function () {
                    if (self._status.status !== 'connecting') {
                        self.set_connection_status('disconnected');
                    }
                }).always(function () {
                setTimeout(status, 5000);
            });
        }

        this.set_connection_status = function (status, drivers) {
            var oldstatus = this._status;
            var newstatus = {};
            newstatus.status = status;
            newstatus.drivers = status === 'disconnected' ? {} : oldstatus.drivers;
            newstatus.drivers = drivers ? drivers : newstatus.drivers;
            this._status = newstatus;
        }

        this.message = function (name, params, opts) {
            var callbacks = this.notifications[name] || [];
            for (var i = 0; i < callbacks.length; i++) {
                callbacks[i](params, opts);
            }
            if (this._status.status !== 'disconnected') {
                return this.connection.rpc('/hw_proxy/' + name, params || {}, opts || {});
            } else {
                return (new $.Deferred()).reject();
            }
        }

        this.keepalive = function () {
            var self = this;

            function status() {
                self.connection.rpc('/hw_proxy/status_json', {}, {timeout: 2500})
                    .then(function (driver_status) {
                        self.set_connection_status('connected', driver_status);
                    }, function () {
                        if (self._status.status !== 'connecting') {
                            self.set_connection_status('disconnected');
                        }
                    }).always(function () {
                    setTimeout(status, 5000);
                });
            }

            if (!this.keptalive) {
                this.keptalive = true;
                status();
            }
        }

        this.print = function (receipt, onSuccess, onError) {
            var self = this;

            if (receipt) {
                this.receipt_queue.push(receipt);
            }

            function send_printing_job() {
                if (self.receipt_queue.length > 0) {
                    var r = self.receipt_queue.shift();
                    self.message('print_xml_receipt', {receipt: r}, {timeout: 5000})
                        .then(function () {
                            if (typeof onSuccess == 'function') {
                                onSuccess();
                            }
                            send_printing_job();
                        }, function (error) {
                            if (error) {
                                if (typeof onError == 'function') {
                                    onError(self._status, error);
                                }
                                return;
                            }
                            self.receipt_queue.unshift(r);
                        });
                }
            }

            send_printing_job();
        }

        this.isConnected = function () {
            return this._status.status === 'connected';
        }

    }

    window.posbox = posbox;

    return posbox;

});