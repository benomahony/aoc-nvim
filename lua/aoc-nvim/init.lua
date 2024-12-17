local M = {}

-- Setup function with defaults
M.setup = function(opts)
	opts = opts or {}

	-- Set session cookie if provided
	if opts.session_cookie then
		vim.g.aoc_session_cookie = opts.session_cookie
	end

	-- Register any additional mappings
	if opts.mappings then
		for lhs, rhs in pairs(opts.mappings) do
			vim.keymap.set("n", lhs, rhs, { silent = true })
		end
	end
end

return M
