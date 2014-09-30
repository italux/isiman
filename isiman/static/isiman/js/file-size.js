/* Plugin for sorting by KB,MB,B,Bytes.
     * http://datatables.net/plug-ins/sorting extended to deal with:
     *    560 kb / quota;
     *    5.02 MB
     *    0 bytes
     */
    jQuery.fn.dataTableExt.oSort['file-size-asc']  = function(a,b) {

        // grab number at the front of the string.
        var x = parseFloat(a); if (isNaN(x)) { x = -1; }
        var y = parseFloat(b); if (isNaN(y)) { y = -1; }

        // trim any "quota"
        a = a.replace(/\s+?\/.*/,'')
        b = b.replace(/\s+?\/.*/,'')

        var x_unit = a.match(/PB/i) ? 1024 * 1024 * 1024 * 1024 * 1024
                   : a.match(/TB/i) ? 1024 * 1024 * 1024 * 1024
                   : a.match(/GB/i) ? 1024 * 1024 * 1024
                   : a.match(/MB/i) ? 1024 * 1024
                   : a.match(/KB/i) ? 1024
                   : 1;
        var y_unit = b.match(/PB/i) ? 1024 * 1024 * 1024 * 1024 * 1024
                   : b.match(/TB/i) ? 1024 * 1024 * 1024 * 1024
                   : b.match(/GB/i) ? 1024 * 1024 * 1024
                   : b.match(/MB/i) ? 1024 * 1024
                   : b.match(/KB/i) ? 1024
                   : 1;

        x = parseInt( parseFloat(x) * x_unit ) || 0;
        y = parseInt( parseFloat(y) * y_unit ) || 0;

        return ((x < y) ? -1 : ((x > y) ?  1 : 0));
    };

    jQuery.fn.dataTableExt.oSort['file-size-desc'] = function(a,b) {
        return jQuery.fn.dataTableExt.oSort['file-size-asc'](b,a);
    };
