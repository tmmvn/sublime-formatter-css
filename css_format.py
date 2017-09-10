#!/usr/bin/python
# encoding: utf-8
#
# CSS Formatter for Sublime Text
#
# Author: Mutian Wang <mutian@me.com>

import sublime, sublime_plugin, sys, os, re

if sys.version_info < (3, 0):
	# ST2, Python 2.6
	from libs.cssformatter import CssFormater
else:
	# ST3, Python 3.3
	from .libs.cssformatter import CssFormater


class CssFormatCommand(sublime_plugin.TextCommand):

	def run(self, edit, action='compact', detectSel=True):
		view = self.view

		if view.is_loading():
			sublime.status_message('Waiting for loading.')
			return False

		# load settings
		global_settings = sublime.load_settings('CSS Format.sublime-settings')
		indentation = view.settings().get('indentation', global_settings.get('indentation', '\t'))
		expand_block_break = view.settings().get('expand_block_break', global_settings.get('expand_block_break', '\n\n'))

		# instantiate formatter
		formatter = CssFormater(indentation, expand_block_break)

		selection = view.sel()[0]
		if detectSel and len(selection) > 0:
			self.format_selection(formatter, action, edit)
		else:
			self.format_whole_file(formatter, action, edit)

	def format_selection(self, formatter, action, edit):
		view = self.view
		regions = []

		for sel in view.sel():
			region = sublime.Region(
				view.line(min(sel.a, sel.b)).a,  # line start of first line
				view.line(max(sel.a, sel.b)).b   # line end of last line
			)
			code = view.substr(region)
			code = formatter.run(code, action)
			#view.sel().clear()
			view.replace(edit, region, code)

	def format_whole_file(self, formatter, action, edit):
		view = self.view
		region = sublime.Region(0, view.size())
		code = view.substr(region)
		code = formatter.run(code, action) + '\n'
		view.replace(edit, region, code)

	def is_visible(self):
		view = self.view
		file_name = view.file_name()
		syntax_path = view.settings().get('syntax')
		suffix_array = ['css', 'sass', 'scss', 'less', 'html', 'htm']
		suffix = ''
		syntax = ''
		
		if file_name != None: # file exists, pull syntax type from extension
			suffix = os.path.splitext(file_name)[1][1:]
		if syntax_path != None:
			syntax = os.path.splitext(syntax_path)[0].split('/')[-1].lower()
		return suffix in suffix_array or syntax in suffix_array


class FormatOnSave(sublime_plugin.EventListener):

	def on_pre_save(self, view):
		global_settings = sublime.load_settings('CSS Format.sublime-settings')

		should_format = view.settings().get('format_on_save', global_settings.get('format_on_save', False))
		if not should_format:
			return

		file_filter = view.settings().get('format_on_save_filter', global_settings.get('format_on_save_filter', '\.(css|sass|scss|less)$'))
		if not re.search(file_filter, view.file_name()):
			return

		format_action = view.settings().get('format_on_save_action', global_settings.get('format_on_save_action', 'expand'))
		if not format_action:
			return

		view.run_command('css_format', {'action': format_action, 'detectSel': False})
