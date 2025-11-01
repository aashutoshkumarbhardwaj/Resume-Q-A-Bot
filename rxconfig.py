import reflex as rx

# Explicitly disable the SitemapPlugin to avoid the startup warning when the
# plugin is not being used in this project. If you later want sitemap
# generation, remove `disable_plugins` and add `rx.plugins.sitemap.SitemapPlugin()`
# to the `plugins` list instead.
config = rx.Config(
	app_name="app",
	plugins=[rx.plugins.TailwindV3Plugin()],
	disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
