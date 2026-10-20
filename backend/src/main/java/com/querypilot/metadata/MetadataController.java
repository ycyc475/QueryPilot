package com.querypilot.metadata;

import com.querypilot.common.ApiResponse;
import com.querypilot.metadata.dto.SchemaDto;
import com.querypilot.metadata.dto.SearchResultDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/datasets/{datasetId}")
public class MetadataController {

    private final MetadataService metadataService;
    private final SemanticSearchService semanticSearchService;

    public MetadataController(MetadataService metadataService, SemanticSearchService semanticSearchService) {
        this.metadataService = metadataService;
        this.semanticSearchService = semanticSearchService;
    }

    @GetMapping("/schema")
    public ApiResponse<SchemaDto> schema(@PathVariable Long datasetId) {
        return ApiResponse.ok(metadataService.getSchema(datasetId));
    }

    @GetMapping("/semantic-search")
    public ApiResponse<SearchResultDto> search(@PathVariable Long datasetId, @RequestParam("q") String q) {
        return ApiResponse.ok(semanticSearchService.search(datasetId, q));
    }
}
