<?php
/*
 * Child copy of growth/template-parts/site-header.php.
 * Only change: the page title is the page's H1 (it was an H3, which left most pages with no H1),
 * unless the page content already carries its own H1, in which case the title stays an H3.
 */
$monem_title_tag = 'h1';
if ( is_singular() ) {
	$monem_raw = (string) get_post_field( 'post_content', get_queried_object_id() ) . (string) get_post_meta( get_queried_object_id(), '_elementor_data', true );
	if ( false !== stripos( $monem_raw, '<h1' ) || false !== strpos( $monem_raw, '"header_size":"h1"' ) ) {
		$monem_title_tag = 'h3';
	}
}
?>
<header class="header-area" >
    <div class="header-content">
        <div class="container">
            <div class="row">
                <div class="col-xs-12 col-md-9">
                    <<?php echo $monem_title_tag; ?> class="page-title"><?php echo growth_page_title(); ?></<?php echo $monem_title_tag; ?>>
                    <?php              
                    if ( class_exists( 'Redux' ) ) {
                        global $growth_opt;
                    }else{
                        $growth_opt                         = array();
                        $growth_opt['breadcrumb_home']      = 'Home';
                        $growth_opt['breadcrumb_separator'] = '|';
                        $growth_opt['sub_title_format']     = 1;
                    }

                    if( $growth_opt['sub_title_format'] == 1 ){
                        echo '<div class="sub-title site-description">'.get_bloginfo( 'description' ) .'</div>';
                    }elseif($growth_opt['sub_title_format'] == 2 and function_exists('growth_breadcrumb') ){
                        echo growth_breadcrumb($growth_opt['breadcrumb_home'],$growth_opt['breadcrumb_separator']);
                    }elseif($growth_opt['sub_title_format'] == 3 and !empty($growth_opt['custom_sub_title']) ){
                        echo '<div class="sub-title">'. wp_kses_post($growth_opt['custom_sub_title']) .'</div>';
                    }
                    ?>
                </div>
            </div>
        </div>
    </div>
</header>
