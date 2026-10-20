package com.querypilot.dataset.dto;

import com.querypilot.dataset.Dataset;

public record DatasetDto(Long id, String name, String description, DatasetSourceDto source) {

    public static DatasetDto from(Dataset dataset) {
        DatasetSourceDto source = new DatasetSourceDto(
                dataset.getSource().getId(),
                dataset.getSource().getName(),
                dataset.getSource().getDbType());
        return new DatasetDto(dataset.getId(), dataset.getName(), dataset.getDescription(), source);
    }
}
