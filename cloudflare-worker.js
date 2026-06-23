// Cloudflare Worker - 营业额分析报告存储服务
// 部署后替换 HTML 中的 API 地址即可

// KV 命名空间绑定名称（在 Cloudflare 控制台绑定）
const KV_NAMESPACE = 'REPORT_KV';

export default {
  async fetch(request, env, ctx) {
    // 允许跨域
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // POST /save-report - 保存报告
    if (path === '/save-report' && request.method === 'POST') {
      try {
        const data = await request.json();
        
        if (!data.report_id) {
          data.report_id = 'rpt_' + Date.now().toString(36);
        }
        
        // 添加时间戳
        const reportData = {
          ...data,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        
        // 存储到 KV
        await env[KV_NAMESPACE].put(data.report_id, JSON.stringify(reportData));
        
        return new Response(JSON.stringify({
          success: true,
          report_id: data.report_id,
          message: 'Report saved successfully'
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
        
      } catch (error) {
        return new Response(JSON.stringify({
          success: false,
          error: error.message
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // GET /get-report/:id - 获取报告
    if (path.startsWith('/get-report/') && request.method === 'GET') {
      try {
        const reportId = path.replace('/get-report/', '');
        
        const data = await env[KV_NAMESPACE].get(reportId);
        
        if (!data) {
          return new Response(JSON.stringify({
            success: false,
            error: 'Report not found'
          }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          });
        }
        
        return new Response(JSON.stringify({
          success: true,
          data: JSON.parse(data)
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
        
      } catch (error) {
        return new Response(JSON.stringify({
          success: false,
          error: error.message
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    // 健康检查
    if (path === '/health') {
      return new Response(JSON.stringify({
        status: 'ok',
        timestamp: new Date().toISOString()
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({
      error: 'Not found',
      available_routes: ['/save-report (POST)', '/get-report/:id (GET)', '/health (GET)']
    }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
};
