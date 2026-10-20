package com.querypilot.admin;

import com.querypilot.common.ApiResponse;
import com.querypilot.metadata.MetadataAdminService;
import com.querypilot.metadata.dto.ColumnDto;
import com.querypilot.metadata.dto.ColumnUpdateRequest;
import com.querypilot.metadata.dto.MetricDto;
import com.querypilot.metadata.dto.MetricUpdateRequest;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 管理员接口（/api/admin/** 需 ADMIN 角色，见 SecurityConfig）。
 */
@RestController
@RequestMapping("/api/admin")
public class AdminMetadataController {

    private final MetadataAdminService adminService;

    public AdminMetadataController(MetadataAdminService adminService) {
        this.adminService = adminService;
    }

    @PutMapping("/metrics/{id}")
    public ApiResponse<MetricDto> updateMetric(@PathVariable Long id,
                                               @RequestBody MetricUpdateRequest request) {
        return ApiResponse.ok(adminService.updateMetric(id, request));
    }

    @PutMapping("/columns/{id}")
    public ApiResponse<ColumnDto> updateColumn(@PathVariable Long id,
                                               @RequestBody ColumnUpdateRequest request) {
        return ApiResponse.ok(adminService.updateColumn(id, request));
    }
}
