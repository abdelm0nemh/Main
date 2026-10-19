<?php
/**
 * Abdelmonem Hassan: what search engines and AI assistants read about the person behind this site.
 *
 * 1. One Person entity (#person) carries everything: photo, profiles, skills, education, certificates.
 *    AIOSEO prints a second Person for the author archive and a Gravatar placeholder as the photo;
 *    both are folded into the one entity so every page and post points at the same person.
 * 2. The About page is a ProfilePage, the home page is about the person, the website has its real name.
 * 3. Service and price nodes on the services and media buying pages, read from the visible
 *    pricing tables so the markup can never disagree with the page.
 * 4. FAQPage from any visible accordion or toggle that holds two or more questions.
 * 5. Booking and template screens stay out of search; the user list stays out of the public REST API.
 * 6. /llms.txt is written live from this profile and the published pages, so it never goes stale.
 *
 * Removing the require in functions.php returns everything to AIOSEO's defaults.
 *
 * @package growth-child
 */

defined( 'ABSPATH' ) || exit;

/* The person. Change a fact here and it changes in the schema and in llms.txt. */
function monem_person() {
	return apply_filters(
		'monem_person',
		array(
			'name'          => 'Abdelmonem Hassan',
			'alternateName' => array( 'Monem', 'Abdelmonem H.', 'عبدالمنعم حسن' ),
			'jobTitle'      => 'Digital Marketing Expert and Performance Media Buyer',
			'description'   => 'Abdelmonem Hassan (Monem) is a freelance digital marketing expert and performance media buyer with an MBA in Marketing. He plans, runs and reports paid campaigns on Meta (Facebook and Instagram), Google, TikTok, Snapchat and LinkedIn for e-commerce and lead generation businesses, and builds the SEO, content, email and automation work around them. He works with clients remotely, worldwide, in English and Arabic.',
			'image'         => 3209,
			'email'         => 'info@abdelmonemhassan.com',
			'sameAs'        => array(
				'https://www.linkedin.com/in/abdelm0nemh/',
				'https://www.instagram.com/abdelm0nemh/',
				'https://www.facebook.com/Abdelm0nemH/',
				'https://www.upwork.com/freelancers/abdelm0nemh',
				'https://www.freelancer.com/u/abdellmnem',
			),
			'knowsAbout'    => array(
				'Media buying',
				'Performance marketing',
				'Meta Ads (Facebook and Instagram advertising)',
				'Google Ads',
				'TikTok Ads',
				'Snapchat Ads',
				'LinkedIn Ads',
				'Conversion tracking',
				'Marketing analytics and reporting',
				'E-commerce marketing',
				'Lead generation',
				'Search engine optimization',
				'Content marketing',
				'Email marketing',
				'Marketing strategy',
				'Marketing automation',
			),
			'knowsLanguage' => array( 'English', 'Arabic' ),
			'alumniOf'      => array(
				'@type'  => 'CollegeOrUniversity',
				'name'   => 'Arab Academy for Science, Technology and Maritime Transport',
				'sameAs' => 'https://aast.edu/',
			),
			// Certificates shown in the "My Certificates" section of the About page.
			'credentials'   => array(
				array( 'Google Ads Search Certification', 'Google' ),
				array( 'Google Ads Display Certification', 'Google' ),
				array( 'Google Ads Video Certification', 'Google' ),
				array( 'Google Ads Fundamentals', 'Google' ),
				array( 'Inbound Certification', 'HubSpot Academy' ),
				array( 'Email Marketing Certification', 'HubSpot Academy' ),
				array( 'Digital Marketing Nanodegree', 'Udacity' ),
				array( 'Advanced Digital Marketing', 'Udacity' ),
				array( 'Digital Freelancer Nanodegree', 'Udacity' ),
				array( 'Search Engine Optimization Certification', 'eMarketing Institute' ),
				array( 'Social Media Marketing Certification', 'eMarketing Institute' ),
			),
		)
	);
}

function monem_person_id() {
	return home_url( '/#person' );
}

/* Pages with a role in the markup. IDs, so renaming a page never breaks it. */
function monem_page_ids() {
	return apply_filters(
		'monem_page_ids',
		array(
			'about'        => 906,
			'services'     => 2040,
			'contact'      => 875,
			'consultation' => 2361,
			'portfolio'    => 1288,
			'blog'         => 30,
			'packages'     => array(
				2884 => 'Focused budget',
				2894 => 'Expansion budget',
				2899 => 'Growth budget',
			),
			'no_index'     => array( 3973, 2855 ), // Meeting Schedule (same booking as /consultation/) and the older packages page.
		)
	);
}

/* The Person node, built once. */
function monem_person_node() {
	$p    = monem_person();
	$node = array(
		'@type'         => 'Person',
		'@id'           => monem_person_id(),
		'name'          => $p['name'],
		'alternateName' => $p['alternateName'],
		'url'           => home_url( '/' ),
		'jobTitle'      => $p['jobTitle'],
		'description'   => $p['description'],
		'email'         => 'mailto:' . $p['email'],
		'knowsAbout'    => $p['knowsAbout'],
		'knowsLanguage' => $p['knowsLanguage'],
		'alumniOf'      => $p['alumniOf'],
		'sameAs'        => $p['sameAs'],
		'mainEntityOfPage' => array( '@id' => get_permalink( monem_page_ids()['about'] ) . '#webpage' ),
	);
	$img = wp_get_attachment_image_src( $p['image'], 'full' );
	if ( $img ) {
		$node['image'] = array(
			'@type'   => 'ImageObject',
			'@id'     => home_url( '/#personImage' ),
			'url'     => $img[0],
			'width'   => (int) $img[1],
			'height'  => (int) $img[2],
			'caption' => $p['name'],
		);
	}
	foreach ( $p['credentials'] as $c ) {
		$node['hasCredential'][] = array(
			'@type'              => 'EducationalOccupationalCredential',
			'name'               => $c[0],
			'credentialCategory' => 'certificate',
			'recognizedBy'       => array( '@type' => 'Organization', 'name' => $c[1] ),
		);
	}
	return $node;
}

/* Visible pricing tables on a page: [ [title, note, price, period], ... ]. Hidden widgets are skipped. */
function monem_price_tables( $post_id ) {
	$tree = json_decode( (string) get_post_meta( $post_id, '_elementor_data', true ), true );
	if ( ! is_array( $tree ) ) {
		return array();
	}
	$rows = array();
	$walk = function ( $nodes, $hidden ) use ( &$walk, &$rows ) {
		foreach ( (array) $nodes as $n ) {
			$s    = isset( $n['settings'] ) && is_array( $n['settings'] ) ? $n['settings'] : array();
			$hide = $hidden || ( ! empty( $s['hide_desktop'] ) && ! empty( $s['hide_mobile'] ) );
			if ( ! $hide && isset( $n['widgetType'] ) && 'growth-pricing-table-addons' === $n['widgetType'] && isset( $s['growth_price'] ) && is_numeric( $s['growth_price'] ) ) {
				$rows[] = array(
					trim( wp_strip_all_tags( (string) ( $s['pricing_title'] ?? '' ) ) ),
					trim( wp_strip_all_tags( (string) ( $s['price_content_editor'] ?? '' ) ) ),
					(float) $s['growth_price'],
					trim( (string) ( $s['growth_period'] ?? '' ) ),
				);
			}
			if ( ! empty( $n['elements'] ) ) {
				$walk( $n['elements'], $hide );
			}
		}
	};
	$walk( $tree, false );
	return $rows;
}

/* Visible accordion / toggle questions on a page: [ [q, a], ... ]. */
function monem_page_faq( $post_id ) {
	// Posts list their closing questions in _monem_faq (JSON list of {q, a}); the same questions are printed in the post.
	$saved = json_decode( (string) get_post_meta( $post_id, '_monem_faq', true ), true );
	if ( is_array( $saved ) && $saved ) {
		$items = array();
		foreach ( $saved as $f ) {
			if ( ! empty( $f['q'] ) && ! empty( $f['a'] ) ) {
				$items[] = array( wp_strip_all_tags( $f['q'] ), wp_strip_all_tags( $f['a'] ) );
			}
		}
		return $items;
	}
	$raw = (string) get_post_meta( $post_id, '_elementor_data', true );
	if ( '' === $raw || false !== strpos( $raw, 'FAQPage' ) ) {
		return array();
	}
	$tree  = json_decode( $raw, true );
	$items = array();
	$walk  = function ( $nodes, $hidden ) use ( &$walk, &$items ) {
		foreach ( (array) $nodes as $n ) {
			$s    = isset( $n['settings'] ) && is_array( $n['settings'] ) ? $n['settings'] : array();
			$hide = $hidden || ( ! empty( $s['hide_desktop'] ) && ! empty( $s['hide_mobile'] ) );
			if ( ! $hide && isset( $n['widgetType'] ) && in_array( $n['widgetType'], array( 'accordion', 'toggle' ), true ) && ! empty( $s['tabs'] ) ) {
				foreach ( $s['tabs'] as $t ) {
					$q = trim( wp_strip_all_tags( (string) ( $t['tab_title'] ?? '' ) ) );
					$a = trim( preg_replace( '/\s+/u', ' ', wp_strip_all_tags( (string) ( $t['tab_content'] ?? '' ) ) ) );
					if ( '' !== $q && '' !== $a ) {
						$items[] = array( $q, $a );
					}
				}
			}
			if ( ! empty( $n['elements'] ) ) {
				$walk( $n['elements'], $hide );
			}
		}
	};
	if ( is_array( $tree ) ) {
		$walk( $tree, false );
	}
	return $items;
}

/* 1-4. The schema graph */
add_filter(
	'aioseo_schema_output',
	function ( $graph ) {
		if ( ! is_array( $graph ) ) {
			return $graph;
		}
		$pid       = monem_person_id();
		$ids       = monem_page_ids();
		$author_id = array();

		// Drop AIOSEO's own Person nodes; remember their @ids so references can be pointed at #person.
		foreach ( $graph as $k => $node ) {
			if ( is_array( $node ) && 'Person' === ( $node['@type'] ?? '' ) ) {
				if ( isset( $node['@id'] ) && $node['@id'] !== $pid ) {
					$author_id[] = $node['@id'];
				}
				unset( $graph[ $k ] );
			}
		}
		$swap = function ( &$value ) use ( &$swap, $author_id, $pid ) {
			if ( ! is_array( $value ) ) {
				return;
			}
			foreach ( $value as &$v ) {
				if ( is_array( $v ) && isset( $v['@id'] ) && in_array( $v['@id'], $author_id, true ) && count( $v ) <= 2 ) {
					$v = array( '@id' => $pid );
					continue;
				}
				$swap( $v );
			}
			unset( $v );
		};
		$swap( $graph );
		$graph   = array_values( $graph );
		$graph[] = monem_person_node();

		$is_about = is_page( $ids['about'] );
		foreach ( $graph as $k => $node ) {
			if ( ! is_array( $node ) ) {
				continue;
			}
			$type = $node['@type'] ?? '';
			if ( 'WebSite' === $type ) {
				$graph[ $k ]['name']          = 'Abdelmonem Hassan';
				$graph[ $k ]['alternateName'] = 'Monem';
				$graph[ $k ]['publisher']     = array( '@id' => $pid );
			}
			if ( 'WebPage' === $type && $is_about ) {
				$graph[ $k ]['@type']      = 'ProfilePage';
				$graph[ $k ]['mainEntity'] = array( '@id' => $pid );
			}
			if ( 'WebPage' === $type && is_front_page() ) {
				$graph[ $k ]['about'] = array( '@id' => $pid );
			}
			if ( in_array( $type, array( 'BlogPosting', 'Article' ), true ) ) {
				$graph[ $k ]['author']    = array( '@id' => $pid );
				$graph[ $k ]['publisher'] = array( '@id' => $pid );
			}
		}

		// 3. Services
		if ( is_page( $ids['services'] ) ) {
			$graph[] = array(
				'@type'       => 'Service',
				'@id'         => get_permalink() . '#service',
				'name'        => 'Freelance digital marketing services',
				'serviceType' => 'Digital marketing',
				'description' => 'Media buying, PPC and search ads, social media marketing, SEO, content marketing, email marketing, e-commerce marketing, strategic planning, research and analysis, and consultation, delivered by Abdelmonem Hassan as a freelancer.',
				'provider'    => array( '@id' => $pid ),
				'areaServed'  => 'Worldwide',
				'url'         => get_permalink(),
			);
		}
		$package_pages = $ids['packages'];
		if ( is_singular( 'page' ) && isset( $package_pages[ get_queried_object_id() ] ) ) {
			$offers = array();
			foreach ( monem_price_tables( get_queried_object_id() ) as $row ) {
				$offers[] = array(
					'@type'         => 'Offer',
					'name'          => $row[0],
					'description'   => trim( $row[1] . ' Media buying management fee, billed ' . strtolower( trim( $row[3], '/ ' ) ) . 'ly.' ),
					'price'         => $row[2],
					'priceCurrency' => 'USD',
					'url'           => get_permalink(),
				);
			}
			$service = array(
				'@type'       => 'Service',
				'@id'         => get_permalink() . '#service',
				'name'        => 'Media buying management: ' . $package_pages[ get_queried_object_id() ],
				'serviceType' => 'Media buying',
				'description' => wp_strip_all_tags( get_the_title() ) . ': paid campaign planning, setup, creative testing, optimisation and monthly reporting on Meta, Google, TikTok, Snapchat or LinkedIn, priced by monthly ad budget.',
				'provider'    => array( '@id' => $pid ),
				'areaServed'  => 'Worldwide',
				'url'         => get_permalink(),
			);
			if ( $offers ) {
				$service['hasOfferCatalog'] = array(
					'@type'           => 'OfferCatalog',
					'name'            => wp_strip_all_tags( get_the_title() ) . ' packages',
					'itemListElement' => $offers,
				);
			}
			$graph[] = $service;
		}

		// 4. FAQ
		if ( is_singular() || is_front_page() ) {
			$faq = monem_page_faq( get_queried_object_id() );
			if ( count( $faq ) >= 2 ) {
				$entities = array();
				foreach ( $faq as $f ) {
					$entities[] = array(
						'@type'          => 'Question',
						'name'           => $f[0],
						'acceptedAnswer' => array( '@type' => 'Answer', 'text' => $f[1] ),
					);
				}
				$graph[] = array(
					'@type'      => 'FAQPage',
					'@id'        => get_permalink( get_queried_object_id() ) . '#faq',
					'mainEntity' => $entities,
				);
			}
		}

		return array_values( $graph );
	},
	20
);

/* 5. Booking duplicates, the old packages page and builder templates stay out of search; links are still followed. */
add_filter(
	'aioseo_robots_meta',
	function ( $attrs ) {
		$ids = monem_page_ids();
		if ( is_page( $ids['no_index'] ) || is_singular( array( 'element-ready-hf-tpl', 'e-floating-buttons', 'elementor_library' ) ) ) {
			$attrs['noindex'] = 'noindex';
		}
		return $attrs;
	},
	99
);
add_filter(
	'aioseo_sitemap_exclude_posts',
	function ( $ids ) {
		return array_values( array_unique( array_merge( (array) $ids, monem_page_ids()['no_index'], array( monem_page_ids()['consultation'], 3091 ) ) ) );
	},
	10,
	1
);

/* Keep the user list out of the public REST API. Logged-in editors keep it. */
add_filter(
	'rest_endpoints',
	function ( $endpoints ) {
		if ( is_user_logged_in() ) {
			return $endpoints;
		}
		foreach ( array_keys( $endpoints ) as $route ) {
			if ( 0 === strpos( $route, '/wp/v2/users' ) ) {
				unset( $endpoints[ $route ] );
			}
		}
		return $endpoints;
	},
	99
);

/* 6. llms.txt, written live. .htaccess sends /llms.txt here even if AIOSEO leaves a static file behind. */
function monem_llms_txt() {
	$p    = monem_person();
	$ids  = monem_page_ids();
	$link = function ( $id, $desc = '' ) {
		if ( 'publish' !== get_post_status( $id ) ) {
			return '';
		}
		if ( '' === $desc ) {
			$desc = (string) aioseo()->meta->description->getDescription( get_post( $id ) );
		}
		$desc = trim( html_entity_decode( wp_strip_all_tags( $desc ), ENT_QUOTES | ENT_HTML5, 'UTF-8' ) );
		return '- [' . html_entity_decode( wp_strip_all_tags( get_the_title( $id ) ), ENT_QUOTES | ENT_HTML5, 'UTF-8' ) . '](' . get_permalink( $id ) . ')' . ( '' !== $desc ? ': ' . $desc : '' ) . "\n";
	};

	$out  = '# ' . $p['name'] . "\n\n";
	$out .= '> ' . $p['description'] . "\n\n";
	$out .= "This is the personal website of Abdelmonem Hassan, also known as Monem. It is a person, not an agency: the work described here is done by him directly.\n\n";
	$out .= "## Key facts\n\n";
	$out .= '- Role: ' . $p['jobTitle'] . "\n";
	$out .= "- Education: MBA in Marketing; " . $p['alumniOf']['name'] . "\n";
	$out .= '- Languages: ' . implode( ', ', $p['knowsLanguage'] ) . "\n";
	$out .= "- Works: remotely, worldwide\n";
	$out .= '- Contact: ' . $p['email'] . ' or book a call at ' . get_permalink( $ids['consultation'] ) . "\n";
	$out .= '- Skills: ' . implode( ', ', $p['knowsAbout'] ) . "\n";
	$out .= '- Certificates: ' . implode( ', ', array_map( function ( $c ) { return $c[0] . ' (' . $c[1] . ')'; }, $p['credentials'] ) ) . "\n";
	$out .= '- Profiles: ' . implode( ', ', $p['sameAs'] ) . "\n\n";

	$out .= "## Main pages\n\n";
	$out .= $link( (int) get_option( 'page_on_front' ) );
	foreach ( array( 'about', 'services', 'portfolio', 'contact', 'blog' ) as $key ) {
		$out .= $link( $ids[ $key ] );
	}

	$out .= "\n## Media buying packages\n\n";
	$out .= "Prices are the monthly management fee in US dollars. The advertising budget itself is paid by the client to the ad platform and is not included.\n\n";
	foreach ( $ids['packages'] as $id => $label ) {
		if ( 'publish' !== get_post_status( $id ) ) {
			continue;
		}
		$out .= '### ' . $label . ' (' . get_permalink( $id ) . ")\n\n";
		foreach ( monem_price_tables( $id ) as $row ) {
			$out .= '- ' . $row[0] . ': $' . rtrim( rtrim( number_format( $row[2], 2, '.', '' ), '0' ), '.' ) . ' ' . $row[3] . ( '' !== $row[1] ? ' (' . $row[1] . ')' : '' ) . "\n";
		}
		$out .= "\n";
	}

	$out .= "## Case studies and work samples\n\n";
	foreach ( get_posts( array( 'post_type' => 'portfolio', 'post_status' => 'publish', 'numberposts' => 40, 'orderby' => 'date', 'order' => 'DESC' ) ) as $post ) {
		$out .= $link( $post->ID, ' ' );
	}

	$out .= "\n## Articles\n\n";
	foreach ( get_posts( array( 'post_type' => 'post', 'post_status' => 'publish', 'numberposts' => 100, 'orderby' => 'date', 'order' => 'DESC' ) ) as $post ) {
		$out .= $link( $post->ID );
	}

	$out .= "\n## Other languages\n\nThe site is also available in Arabic at " . home_url( '/ar/' ) . ' and in Spanish at ' . home_url( '/es/' ) . ".\n\n";
	$out .= '## Sitemap' . "\n\n- " . home_url( '/sitemap.xml' ) . "\n";
	return $out;
}
add_action(
	'init',
	function () {
		$path = (string) wp_parse_url( isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '', PHP_URL_PATH );
		if ( '/llms.txt' !== $path || ! function_exists( 'aioseo' ) ) {
			return;
		}
		$txt = get_transient( 'monem_llms_txt' );
		if ( false === $txt ) {
			$txt = monem_llms_txt();
			set_transient( 'monem_llms_txt', $txt, 6 * HOUR_IN_SECONDS );
		}
		status_header( 200 );
		header( 'Content-Type: text/plain; charset=utf-8' );
		header( 'X-Robots-Tag: noindex' );
		echo $txt; // phpcs:ignore WordPress.Security.EscapeOutput -- text/plain
		exit;
	},
	0
);
add_action(
	'save_post',
	function () {
		delete_transient( 'monem_llms_txt' );
	}
);

/* The name in the home hero is the home page's H1. The Growth text-box widget hard-codes an H2, and its size and spacing are set in Elementor, so the look does not change. */
add_filter(
	'elementor/widget/render_content',
	function ( $content, $widget ) {
		if ( '422d35f' === $widget->get_id() && is_front_page() ) {
			$content = preg_replace( '#<h2 class="title">(.*?)</h2>#s', '<h1 class="title">$1</h1>', $content, 1 );
		}
		return $content;
	},
	10,
	2
);
