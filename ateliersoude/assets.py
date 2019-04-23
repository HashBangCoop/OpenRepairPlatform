from django_assets import Bundle, register

# SCSS
scss_atelier_soude = Bundle(
    'scss/ateliersoude.scss',
    filters='scss',
    output='css/ateliersoude.css',
)
scss_places = Bundle(
    'scss/lib/leaflet.scss', 'scss/places/leaflet_custom.scss',
    'scss/places/custom.scss',
    filters='scss',
    output='css/leaflet_custom.css',
)
scss_detail_place = Bundle(
    'scss/lib/leaflet.scss', 'scss/places/leaflet_custom.scss',
    filters='scss',
    output='css/detail_place.css',
)
scss_auto_complete = Bundle(
    'scss/lib/auto-complete.scss',
    filters='scss',
    output='css/auto-complete.css',
)

# CSS minify
css_atelier_soude = Bundle(
    scss_atelier_soude,
    filters='cssrewrite,cssmin',
    output='css/ateliersoude.min.css'
)
css_places = Bundle(
    scss_places,
    filters='cssrewrite,cssmin',
    output='css/places.min.css'
)
css_detail_place = Bundle(
    scss_detail_place,
    filters='cssrewrite,cssmin',
    output='css/detail_place.min.css'
)
css_auto_complete = Bundle(
    scss_auto_complete,
    filters='cssrewrite,cssmin',
    output='css/auto-complete.min.css'
)

# JS minify
js_places = Bundle(
    'js/lib/leaflet.js', 'js/places/leaflet_custom.js', 'js/places/custom.js',
    filters='jsmin',
    output='js/places/places.min.js'
)
js_create_edit_place = Bundle(
    'js/lib/auto-complete.js', 'js/places/create_edit.js',
    filters='jsmin',
    output='js/places/create-edit.min.js'
)
js_detail_place = Bundle(
    'js/lib/leaflet.js', 'js/places/leaflet_custom.js', 'js/places/detail.js',
    filters='jsmin',
    output='js/places/create-edit.min.js'
)

register('css_ateliersoude', css_atelier_soude)
register('css_places', css_places)
register('css_autocomplete', css_auto_complete)
register('css_detail_place', css_detail_place)
register('js_places', js_places)
register('js_create_edit_place', js_create_edit_place)
register('js_detail_place', js_detail_place)
