package com.example;

import java.util.List;

public record UsgsFeed(String type, List<UsgsFeature> features) {
}
