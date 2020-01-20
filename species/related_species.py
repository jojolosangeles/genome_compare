import pandas as pd
import altair as alt

class RelatedSpecies:
    def __init__(self, df):
        self.df = df
        self.species_df = {}
        self.relationships = df.groupby(['sp', 'chr', 'msp', 'mchr']).size().reset_index().rename(columns={0: 'count'})
        self.chr_order = {}

    def setChromosomeOrder(self, species, chromosomes):
        self.chr_order[species] = chromosomes

    def getSpecies(self, species):
        if species not in self.species_df:
            df = self.df
            temp_df = df[(df['sp'] == species) & (df['msp'] == species)]
            temp_df = temp_df.copy(deep=True)
            temp_df['count'] = 0
            self.species_df[species] = temp_df
        return self.species_df[species]

    def getSpeciesXchr(self, species):
        df = self.getSpecies(species)
        return df[df['chr'] != df['mchr']]

    def getChromosomeRelationships(self, sp1, sp2, min_record_count=0):
        """Count related records between two species.

        Returns DataFrame with fields:

            sp1 -- species 1 chromosome names
            sp2 -- species 2 chromosome names
            count -- count of related records between the two (determined by elasticsearch results, in csv)
        """
        sp1_chr_list = self.chr_order[sp1]
        sp2_chr_list = self.chr_order[sp2]
        ax1chrs = [v1 for v1 in sp1_chr_list for v2 in sp2_chr_list]
        ax2chrs = [v2 for v1 in sp1_chr_list for v2 in sp2_chr_list]
        counts = []
        df = self.relationships
        for ax1_chr, ax2_chr in zip(ax1chrs, ax2chrs):
            xdf = df[(df['sp'] == sp1) &
                     (df['msp'] == sp2) &
                     (df['chr'] == ax1_chr) &
                     (df['mchr'] == ax2_chr)
            ]
            count = 0
            if len(xdf) > 0:
                count = xdf.iloc[0]['count']
            counts.append(count)

        source = pd.DataFrame({sp1: ax1chrs,
                               sp2: ax2chrs,
                               'count': counts})
        if min_record_count > 0:
            source = source[source['count'] >= min_record_count]
        return source

    @staticmethod
    def read_csv(csvFile):
        """Read CSV file that resulted from Elasticsearch scoring of relationships.

        Returns DataFrame with columns:

            sp, chr, loc -- species, chromosome, location
            msp, mchr, mloc -- matching species, chromosome, location
            score -- Elasticsearch scoring
            orientation -- distinguish 'same orientation' from 'inversed' (reverse complement)

        The score, loc, and mloc fields are 'int' data type
        """
        return pd.read_csv(csvFile,
                           index_col=False,
                           dtype={'sp': str, 'chr': str, 'loc': int,
                                  'score': int,
                                  'msp': str, 'mchr': str, 'mloc': int,
                                  'orientation': str})


class SpeciesGraphs:
    def __init__(self, related_species):
        self.related_species = related_species

    def chromosomeRelationships(self, sp1, sp2):
        """Heatmap of related chromosomes between two species"""
        source = self.related_species.getChromosomeRelationships(sp1, sp2)
        ax1_title = f"{sp1} chromosomes"
        ax2_title = f"{sp2} chromosomes"
        chr_map = self.related_species.chr_order
        return alt.Chart(source).mark_rect().encode(
            x=alt.X(f"{sp1}:N", sort=chr_map[sp1], axis=alt.Axis(title=ax1_title, grid=True, ticks=True)),
            y=alt.Y(f"{sp2}:N", sort=chr_map[sp2], axis=alt.Axis(title=ax2_title, grid=True, ticks=True)),
            color=alt.Color('count:Q', title="count")
        )


class ChromosomeGraphs:
    domains = ['same orientation', 'inversed']
    color_scale = alt.Scale(
        domain=domains,
        range=['#6baed6', '#fcae91']
    )

    def __init__(self, related_species):
        self.related_species = related_species

    def comparisionDF(self, species, chromosome, sp2, sp3, min_score=1000, min_records=10):
        """get one or more DataFrame with relationships that meet the conditions"""
        pass

# def cgraph(df, top_species, top_chromosome, middle_species, middle_chromosome, bottom_species, bottom_chromosome,
#            graph_width=600):
#     g = alt.Chart(df).mark_line().encode(
#         x=alt.X('x', axis=alt.Axis(grid=False)),
#         y=alt.Y('y', axis=alt.Axis(grid=False)),
#         x2='x2',
#         y2='y2',
#         color=alt.Color('orientation:N', title='', scale=color_scale)
#     )
#
#     maxes = df.max()
#     maxCenter = maxes['x']
#     maxRest = maxes['x2']
#     maxY = max(maxes['y'], maxes['y2'])
#
#     # here I just want a bar at the top, and text on the right that says:  species, chromosome
#     # top_data + bars, gives me a transparent green bar at top, with no text
#     top_label = f"{top_species}, {top_chromosome}"
#     middle_label = f"{middle_species}, {middle_chromosome}"
#     bottom_label = f"{bottom_species}, {bottom_chromosome}"
#     X_MARGIN = 10
#     Y_MARGIN = 12
#     top_data = pd.DataFrame({
#         'x': [maxRest + X_MARGIN, maxRest + X_MARGIN, maxRest + X_MARGIN],
#         'y': [maxY - Y_MARGIN, int(maxY / 2), Y_MARGIN],
#         'text': [top_label, middle_label, bottom_label]
#     })
#     bars = alt.Chart(top_data).mark_text(
#         stroke='grey',
#         opacity=0.9,
#         fontSize=10,
#         fontStyle="italic",
#         align="left"
#     ).encode(
#         x=alt.X('x:Q'),
#         y=alt.Y('y:Q'),
#         text=alt.Text('text'),
#         color=alt.Color('orientation:N', legend=None, scale=color_scale)
#     )
#
#     x = alt.Chart().mark_text().encode(
#         x=alt.X('x:Q', axis=alt.Axis(title='million bp', grid=False, ticks=True)),
#         y=alt.Y('y:Q', axis=alt.Axis(title='', grid=False, labels=False, ticks=False)),
#         color=alt.Color('orientation:N', legend=alt.Legend(orient="left", title='', symbolType="stroke"),
#                         scale=color_scale)
#     )
#
#     return alt.layer(x, bars, g).configure_view(
#         stroke='transparent',
#         width=graph_width
#     ).configure_axis(grid=False)
#
#
# def sp_to_y(val, top, mid, bot):
#     if val == bot:
#         return 0
#     elif val == mid:
#         return 200
#     else:
#         return 400
#
#
# def mod_df(df, top_sp, top_chr, middle_sp, middle_chr, bottom_sp, bottom_chr, min_score=1000):
#     df = df[df['sp'] == middle_sp]
#     df = df[df['score'] > min_score]
#     df = df[df['chr'] == middle_chr]
#     df = df[(df['mchr'] == top_chr) | (df['mchr'] == bottom_chr)]
#     df['x'] = [x / 1000000 for x in df['loc']]
#     df['x2'] = [x / 1000000 for x in df['mloc']]
#     df['y'] = [sp_to_y(val, top_sp, middle_sp, bottom_sp) for val in df['sp']]
#     df['y2'] = [sp_to_y(val, top_sp, middle_sp, bottom_sp) for val in df['msp']]
#     return df
#
#
# def graph_df(df, top_sp, top_chr, middle_sp, middle_chr, bottom_sp, bottom_chr, min_score=1000, graph_width=600):
#     df = mod_df(df, top_sp, top_chr, middle_sp, middle_chr, bottom_sp, bottom_chr, min_score)
#     return cgraph(df, top_sp, top_chr, middle_sp, middle_chr, bottom_sp, bottom_chr, graph_width)
#
