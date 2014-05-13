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

my $template_file = "rdpclassify.awt.tt";
if (exists $ENV{KB_SERVICE_DIR})
{
    $template_file = "$ENV{KB_SERVICE_DIR}/$ENV{KB_SERVICE_NAME}/$template_file";
}

my($opt, $usage) = describe_options("%c %o input-handle-list",
				    ["list", 'the handle option is a list of handles'],
				    ["output|o=s", "write the output to this file"],
				    ["conf|c=s", 'confidence cutoff', { default => 0.8 }],
				    ["format|f=s", "output format", { default => 'allrank' }],
				    ["gene|g=s", "gene", { default => '16srrna' }]);

my $templ = Template->new({ ABSOLUTE => 1 });

my $handle_list;

if ($opt->list)
{
    my $handle_file = shift @ARGV;

    $handle_list = decode_json(scalar read_file($handle_file));
}
else
{
    $handle_list = [];
    for my $handle_file (@ARGV)
    {
	my $handle = decode_json(scalar read_file($handle_file));
	push(@$handle_list, $handle);
    }
}

my $params = join(" ", -c => $opt->conf, -f => $opt->format, -g => $opt->gene);

my $input_list = join(" ", map { "\@$_->{file_name}" } @$handle_list);

my $jobname = "rdp-classify";
my $user = "username";
my $shock_url = "140.221.85.54:7044";

if (@$handle_list)
{
    $shock_url = $handle_list->[0]->{url};
    $shock_url =~ s,^http://,,;
}

my $project = "project";

my %vars = (parameters => $params,
	    input_list => $input_list,
	    handles => $handle_list,
	    jobname => $jobname,
	    user => $user,
	    shockurl => $shock_url,
	    project => $project,
    );

print STDERR "Expand: " . Dumper($template_file, $opt, \%ENV);

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

