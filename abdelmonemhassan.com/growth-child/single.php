<?php
/* Child copy of growth/single.php. Changes: the post title is the H1 (was H3), and an author box follows the post. */
?><?php

/**
 * The Single Post Template
 *
 * @package growth
 */

get_header();
the_post();

//Populer post view count function
if (function_exists('growth_set_post_views')) {
    growth_set_post_views(get_the_ID());
}

if (class_exists('Redux')) {
    global $growth_opt;
} else {
    $growth_opt                       = array();
    $growth_opt['single_releted_tag'] = true;
    $growth_opt['single_blog_meta']   = $growth_opt['single_post_share'] = false;
    $growth_opt['single_post_nav']    = true;
    $growth_opt['single_author_info'] = true;
    $growth_opt['show_releted_post']  = false;
}

?>
<header class="header-area">
    <div class="header-content">
        <div class="container">
            <div class="row">
                <div class="col-xs-12 col-md-9">
                    <h1 class="page-title"><?php echo growth_page_title(); ?></h1>
                    <div class="sub-title site-description"><?php echo get_the_excerpt(); ?></div>
                </div>
            </div>
        </div>
    </div>
    <div class="single-post-meta">
        <div class="container">
            <div class="start-height">
                <div class="meta-item">
                    <span class="meta-title"><?php esc_html_e('Publish Date', 'growth'); ?></span>
                    <div class="meta-text"><?php echo get_the_date(); ?></div>
                </div>
                <?php if (has_category()) : ?>
                    <div class="meta-item">
                        <span class="meta-title"><?php esc_html_e('Categories', 'growth'); ?></span>
                        <div class="meta-text"><?php echo get_the_category_list(); ?></div>
                    </div>
                <?php endif; ?>
                <div class="meta-item">
                    <span class="meta-title"><?php esc_html_e('Read Time', 'growth'); ?></span>
                    <div class="meta-text"><?php echo growth_reading_time(); ?></div>
                </div>
                <?php if (function_exists('growth_post_share_social')) : ?>
                    <div class="meta-item">
                        <span class="meta-title"><?php esc_html_e('Share', 'growth'); ?></span>
                        <div class="meta-text">
                            <?php
                            growth_post_share_social();
                            ?>
                        </div>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</header>

<div class="single-post-area">
    <div class="post-content-area">
        <div class="container">
            <div class="row">
                <div class="col-xs-12 col-md-10 col-md-offset-1">
                    <?php get_template_part('template-parts/post-formats/post', get_post_format()); ?>
                    <?php get_template_part('template-parts/monem-author-box'); // Child: author box under the post. ?>
                </div>
            </div>
        </div>
    </div>
    <?php if (has_tag() == true and $growth_opt['single_releted_tag'] == true) : ?>
        <div class="post-tag-area">
            <div class="container">
                <div class="single-tags">
                    <div class="section-title-box">
                        <div class="sup-title"><?php esc_html_e('Post Tags', 'growth'); ?></div>
                        <h3 class="title"><?php esc_html_e('Related Tags', 'growth'); ?></h3>
                    </div>
                    <?php echo get_the_tag_list('', ' ', ''); ?>
                </div>
            </div>
        </div>
    <?php endif; ?>
    <?php if ($growth_opt['single_post_nav'] == true and get_the_post_navigation()) : ?>
        <div class="single-post-navigation">
            <div class="container">
                <?php
                // Previous/next post navigation.
                the_post_navigation(array(
                    'next_text' => '<span class="meta-nav">' . esc_html__('Next Post', 'growth') . '</span><h3 class="title">%title</h3>',
                    'prev_text' => '<span class="meta-nav">' . esc_html__('Prev Post', 'growth') . '</span><h3 class="title">%title</h3>',
                ));
                ?>
            </div>
        </div>
    <?php endif;

    $related_tags = wp_get_post_tags(get_the_ID());
    $args = array();
    if ($related_tags) {
        $first_tag = $related_tags[0]->term_id;
        $args = array(
            'tag__in' => array($first_tag),
            'post__not_in' => array(get_the_ID()),
            'posts_per_page' => 4
        );
    }
    $related_query = new WP_Query($args);
    if ($growth_opt['show_releted_post'] == true and $related_query->have_posts()) : ?>
        <div class="related-post-area">
            <div class="container">
                <div class="section-title-box">
                    <div class="sup-title"><?php esc_html_e('My Blog', 'growth'); ?></div>
                    <h3 class="title"><?php esc_html_e('Related Articles', 'growth'); ?></h3>
                </div>
                <div class="related-posts small-blog">
                    <?php
                    while ($related_query->have_posts()) : $related_query->the_post();
                    ?>
                        <div class="post-single">
                            <figure class="post-media"><?php the_post_thumbnail('growth-post-image'); ?></figure>
                            <div class="post-content">
                                <div class="post-meta">
                                    <span class="meta-item">
                                        <span class="icon"><i class="fal fa-clock"></i></span>
                                        <?php echo get_the_date(); ?>
                                    </span>
                                </div>
                                <h2 class="post-title">
                                    <a href="<?php echo get_the_permalink(); ?>" rel="bookmark"><?php echo get_the_title(); ?></a>
                                </h2>
                                <div class="post-desc">
                                    <?php echo wp_trim_words(get_the_content(), 20, ' ...'); ?>
                                </div>
                            </div>
                        </div>
                    <?php
                    endwhile;
                    wp_reset_postdata();
                    ?>
                </div>
            </div>
        </div>
    <?php endif;
    if (comments_open() || get_comments_number()) :
    ?>
        <div class="post-comments-area">
            <div class="container">
                <div class="row">
                    <?php
                    // If comments are open or we have at least one comment, load up the comment template.
                    comments_template();
                    ?>
                </div>
            </div>
        </div>
    <?php endif; ?>
</div>
<?php get_footer(); ?>