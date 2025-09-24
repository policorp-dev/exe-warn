pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'exe_warn'
gnome = import('gnome')

gnome.compile_resources('exe-warn',
  'exe-warn.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'exe-warn.in',
  output: 'exe-warn',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

exe_warn_sources = [
  '__init__.py',
  'main.py',
  'window.py',
]

install_data(exe_warn_sources, install_dir: moduledir)
