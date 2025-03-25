import React from 'react';
import {
  InstantSearch,
  SearchBox,
  Hits,
  SortBy,
  RefinementList,
} from 'react-instantsearch';
import { instantMeiliSearch } from '@meilisearch/instant-meilisearch';
import 'instantsearch.css/themes/satellite-min.css';

const searchClient = instantMeiliSearch(
  import.meta.env.VITE_MEILISEARCH_HOST || 'http://localhost:7700',
  '',
  { primaryKey: 'geonameid' }
);

const Hit = ({ hit }) => (
  <div className="hit-card">
    <h2 className="city-name">{hit.name}</h2>
    <p><strong>Country:</strong> {hit.country}</p>
    <p><strong>Population:</strong> {hit.population.toLocaleString()}</p>
    <p><strong>Timezone:</strong> {hit.timezone}</p>
  </div>
);

const App = () => (
  <div className="app-container">
    <h1 className="title">🌍 World Cities Search</h1>

    <InstantSearch indexName="cities" searchClient={searchClient}>
      <div className="search-panel">
        <div className="filters-panel">
          <h3>Filter by Country</h3>
          <RefinementList attribute="country" searchable />

          <h3>Filter by Timezone</h3>
          <RefinementList attribute="timezone" searchable />
        </div>

        <div className="results-panel">
          <div className="top-bar">
            <SearchBox className="search-box" />
            <SortBy
              items={[
                { label: 'Default', value: 'cities' },
                { label: 'Population ↓', value: 'cities:population:desc' },
                { label: 'Population ↑', value: 'cities:population:asc' },
              ]}
              className="sort-select"
            />
          </div>
          <Hits hitComponent={Hit} />
        </div>
      </div>
    </InstantSearch>
  </div>
);

export default App;
