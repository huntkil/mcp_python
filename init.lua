-- Neovim MCP Server 설정
-- nvim-mcp 플러그인 사용 시

local mcp_config = {
  servers = {
    ["markdown-manager"] = {
      command = "bash",
      args = {"-c", "source .venv/bin/activate && python -m src.server"},
      cwd = "/Users/gukho/Desktop/git/mcp_python"
    }
  }
}

-- nvim-mcp 플러그인 설정 (설치 후)
-- require('mcp').setup(mcp_config)

-- 또는 직접 subprocess로 실행하는 방법
local function run_mcp_server()
  local cmd = "cd /Users/gukho/Desktop/git/mcp_python && source .venv/bin/activate && python -m src.server"
  vim.fn.jobstart(cmd, {
    on_stdout = function(_, data, _)
      if data then
        print("MCP Server: " .. table.concat(data, "\n"))
      end
    end
  })
end

-- 명령어 등록
vim.api.nvim_create_user_command('MCPStart', run_mcp_server, {}) 