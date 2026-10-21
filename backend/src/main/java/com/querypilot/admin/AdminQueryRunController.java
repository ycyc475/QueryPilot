package com.querypilot.admin;

import com.querypilot.common.ApiResponse;
import com.querypilot.conversation.QueryRunRepository;
import com.querypilot.conversation.dto.QueryRunDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 管理员查询审计（PRD §3 查询审计页）：查看 query_runs 历史、耗时、失败原因。
 */
@RestController
@RequestMapping("/api/admin")
public class AdminQueryRunController {

    private final QueryRunRepository queryRunRepository;

    public AdminQueryRunController(QueryRunRepository queryRunRepository) {
        this.queryRunRepository = queryRunRepository;
    }

    @GetMapping("/query-runs")
    public ApiResponse<List<QueryRunDto>> list() {
        return ApiResponse.ok(queryRunRepository.findAllByOrderByIdDesc().stream()
                .map(QueryRunDto::from).toList());
    }
}
