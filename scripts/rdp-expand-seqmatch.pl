use strict;
use Template;
use Getopt::Long::Descriptive;
use File::Slurp;
use Data::Dumper;

use JSON::XS;

#
# Here, input-handle-list is a JSON-formatted dump of
# a list of handle objects.
#

my $template_file = "rdpseqmatch.awt.tt";
if (exists $ENV{KB_SERVICE_DIR})
{
    $template_file = "$ENV{KB_SERVICE_DIR}/$template_file";
}

my($opt, $usage) = describe_options("%c %o reference-file query-file",
                                    ["output|o=s", "Write output to this file"],
                                    ["knn|k=s", "Find k nearest neighbors", { default => 20 }],
                                    ["sab|s=s", "Minimum sab score", { default => 0.5 }],
                                    ["token|t=s", "Data authentication token"]);

my $templ = Template->new({ ABSOLUTE => 1 });

my $ref_handle_file = shift;

my $ref_handle = decode_json(scalar read_file($ref_handle_file));
my $query_handle = decode_json(scalar read_file(shift));

my $ref_file = $ref_handle->{file_name};
my $query_file = $query_handle->{file_name};

my $jobname = "rdp-seqmatch";
my $user = "username";
my $shock_url = $ref_handle->{url};
$shock_url =~ s,^http://,,;

my $outfile_name = $jobname . ".txt";

my $params = join(" ", -k => $opt->knn, -s => $opt->sab, -o => $outfile_name);

my $project = "project";

my %vars = (parameters => $params,
            ref_file => $ref_file,
            query_file => $query_file,
            output_file => $outfile_name,
            ref_handle => $ref_handle,
            query_handle => $query_handle,
            jobname => $jobname,
            user => $user,
            shockurl => $shock_url,
            project => $project,
            token => $opt->token);

if ($opt->output)
{
    open(OUT, ">", $opt->output) or die "Cannot open " . $opt->output . ": $!";
    $templ->process($template_file, \%vars, \*OUT)
        || die $templ->error();
    close(OUT);
}
else
{
    $templ->process($template_file, \%vars)
        || die $templ->error();
}
