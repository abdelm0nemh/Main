<?php
/*
 * Author box under every blog post: who wrote this, why to trust it, and the next step.
 * Text comes from the Biographical Info field in Users > Profile, so it can be edited without code.
 */
$monem_bio = trim( (string) get_the_author_meta( 'description', 2 ) );
if ( '' === $monem_bio ) {
	return;
}
$monem_photo = wp_get_attachment_image_src( 3209, 'thumbnail' );
?>
<aside class="monem-author-box" aria-label="<?php esc_attr_e( 'About the author', 'growth' ); ?>">
	<?php if ( $monem_photo ) : ?>
		<img class="monem-author-photo" src="<?php echo esc_url( $monem_photo[0] ); ?>" width="96" height="96" alt="Abdelmonem Hassan" loading="lazy">
	<?php endif; ?>
	<div class="monem-author-text">
		<div class="monem-author-label"><?php esc_html_e( 'Written by', 'growth' ); ?></div>
		<a class="monem-author-name" href="<?php echo esc_url( get_permalink( 906 ) ); ?>">Abdelmonem Hassan</a>
		<p><?php echo esc_html( $monem_bio ); ?></p>
		<a class="arrow-button" href="<?php echo esc_url( get_permalink( 2361 ) ); ?>"><span class="button-text"><span class="button-title"><?php esc_html_e( 'Book a consultation', 'growth' ); ?></span></span></a>
	</div>
</aside>
