project('exe-warn',
          version: '0.1.0',
    meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

pkg_name = meson.project_name()
pkgdatadir = get_option('prefix') / get_option('datadir') / pkg_name

i18n = import('i18n')
gnome = import('gnome')




subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
