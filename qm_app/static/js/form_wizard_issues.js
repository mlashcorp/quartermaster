
(function($) {
   $(document).ready(function() {
        var removeButton = "<div class='padding-30' ><button id='remove_issue' class='remove_field btn btn-default' type='button'>Remove</button> </div>";
        var remove_risk_button = "<div class='padding-30' ><button id='remove_risk' class='remove_field btn btn-default' type='button'>Remove</button> </div>";
        var remove_test_button = "<div class='padding-30' ><button id='remove_test' class='remove_field btn btn-default' type='button'>Remove</button> </div>";

        $('.add_issue_btn').click(function(e) {
            e.preventDefault();
            $('div.issue_container:last').after($('div.issue_container:first').clone());
            $('div.issue_container:last').append(removeButton);
            $('div.issue_container:last input').each(function(){
            this.value = ''; 
            });

        });

        $('.add_risk_btn').click(function(e) {
            e.preventDefault();
            $('div.risk_container:last').after($('div.risk_container:first').clone());
            $('div.risk_container:last').append(remove_risk_button);
            $('div.risk_container:last input').each(function(){
            this.value = ''; 
            });

        });

        $('.add_test_btn').click(function(e) {
            e.preventDefault();
            $('div.test_container:last').after($('div.test_container:first').clone());
            $('div.test_container:last').append(remove_test_button);
            $('div.test_container:last input').each(function(){
            this.value = ''; 
            });

        });

        $(this).on('click','#remove_issue', function(e) {
            e.preventDefault();
            $(this).closest('div.issue_container').remove();
        });

        $(this).on('click','#remove_risk', function(e) {
            e.preventDefault();
            $(this).closest('div.risk_container').remove();
        });

        $(this).on('click','#remove_test', function(e) {
            e.preventDefault();
            $(this).closest('div.test_container').remove();
        });

        $(".multiple_choice").select2();  
    });
    
})(window.jQuery);




