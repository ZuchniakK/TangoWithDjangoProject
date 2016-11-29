/**
 * Created by konrad on 11/25/16.
 */

	$(document).ready(function() {
        // JQuery code to be added in here.
        $('#likes').click(function () {
            alert(" J-Q-ue-ry!");
            var catid;
            catid = $(this).attr("data-catid");
            $.get('/rango/like_category/', {category_id: catid}, function (data) {
                $('#like_count').html(data);
                $('#likes').hide();
            });

        });

        $('#suggestion').keyup(function(){
            var query;
            query = $(this).val();
            $.get('/rango/suggest/', {suggestion: query}, function(data){
                $('#cats').html(data);
            });
        });

        $('.rango-add').click(function () {
            alert("You clicked the button using JQuery!");
            var catid = $(this).attr("data-catid");
            var url = $(this).attr("data-url");
            var title = $(this).attr("data-title");
            var me = $(this);
            $.get('/rango/add/',
                {category_id: catid, url: url, title: title, suggestion: 'd'}, function (data) {
                    $('.pages').html(data);
                    me.hide();


                });

        });














    })




