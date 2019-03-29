#!/usr/bin/env ruby

require "yaml"
require "medium"
require "ap"
require "openssl"
require "net/http"

POSTS_DIR = "content/posts"
CONFIG = YAML.load_file "external-services.yaml"

SERVICES = {
    "dev" => "DEV",
    "medium" => "Medium",
}

MEDIUM = {
    "header" => "![cover]({{ cover-image }})",
    "footer" => "\n---\n*Originally published at [detunized.net]({{ link }}) on {{ date }}*\n",
}

Post = Struct.new :name,
                  :text,
                  :sha,
                  :front,
                  :original_body,
                  :body,
                  :link

def load_status
    YAML.load_file "status.yaml"
end

def save_status status
    File.open("status.yaml", "w") { |io| io.write status.to_yaml }
end

def permalink front_matter
    date = front_matter["date"].strftime "%Y-%m-%d"
    slug = front_matter["title"].downcase.gsub(/\s+/, "-").gsub(/[^a-z0-9_\-.~]/, "")

    "https://detunized.net/posts/#{date}-#{slug}/"
end

def load_post filename
    name = File.basename(filename)
    text = File.read(filename)
    body = text[/---.*?---\s*(.*)/m, 1]
    front_matter = YAML.load text

    Post.new name,
             text,
             Digest::SHA256.hexdigest(text),
             YAML.load(text),
             body,
             body,
             permalink(front_matter)
end

def format_footer post, template
    template
        .gsub("{{ link }}", post.link)
        .gsub("{{ date }}", post.front["date"].strftime("%B %-d, %Y"))
end

def append_footer post, template
    post.body + format_footer(post, template)
end

def prepare_for_medium post
    cover_image = post.front["cover_image"] || ""
    header = MEDIUM["header"].gsub "{{ cover-image }}", cover_image
    footer = format_footer post, MEDIUM["footer"]

    header + post.body + footer
end

def url_exists? url
    response = Net::HTTP.get_response URI url
    response.code.to_i / 100 == 2
end

def publish_to_dev post
    puts "Posting to DEV"
    "https://dev.to/#{post.name}"
end

def publish_to_medium post
    raise "The original URL '#{post.link}' doesn't exist" if !url_exists? post.link

    puts "Posting #{post.name} to Medium..."
    medium = Medium::Client.new integration_token: CONFIG["medium"]["token"]
    response = medium.posts.create medium.users.me,
                                   title: post.front["title"],
                                   content_format: "markdown",
                                   content: prepare_for_medium(post),
                                   publish_status: "draft",
                                   tags: ["programming"] + post.front["tags"],
                                   canonical_url: post.link

    raise "Network request failed #{response}" if response.status_code / 100 != 2

    response_json = JSON.load response.body
    response_json["data"]["url"]
end

def update_on_dev post
    raise "Update on DEV is not supported"
end

def update_on_medium post
    raise "Update on Medium is not supported"
end

def link status, filename, service
    url = status[File.basename filename][service]["url"]
    fail "Don't have a link for #{filename} on #{service}" if url.nil?

    url
end

status = load_status

files = Dir["#{POSTS_DIR}/*.md"]
    .map { |filename| load_post filename }
    .to_h { |post| [post.name, post] }

to_publish = Hash.new { |hash, key| hash[key] = [] }
to_update = Hash.new { |hash, key| hash[key] = [] }

# Figure out the status of each article
files.each do |name, post|
    SERVICES.each do |service_id, service_name|
        if !status.key?(name) || !status[name].key?(service_id)
            to_publish[service_id] << post
        elsif post.sha != status[name][service_id]["sha256"]
            to_update[service_id] << post
        end
    end
end

have_work = false

to_publish.each do |service, posts|
    if posts.size > 0
        have_work = true
        puts "Will publish #{posts.size} new post(s) to #{SERVICES[service]}"
        puts posts.map { |post| "  - #{post.name}" }
    end
end

to_update.each do |service, posts|
    if posts.size > 0
        have_work = true
        puts "Will update #{posts.size} post(s) on #{SERVICES[service]}"
        puts posts.map { |post| "  - #{post.name}" }
    end
end

exit if !have_work

print "Is this correct? Continue? (y/N) "
exit if gets.chomp != "y"

to_publish.each do |service, posts|
    posts.each do |post|
        begin
            # Convert links to other posts
            post.body = post.original_body.gsub(/{{<\s*ref "(.*)"\s*>}}/) { link status, $1, service }

            url = send "publish_to_#{service}", post
            status[post.name] ||= {}
            status[post.name][service] ||= {}
            status[post.name][service]["url"] = url
            status[post.name][service]["sha256"] = post.sha
        rescue e
            puts "Failed to publish '#{post.name}' to #{SERVICES[service]} #{e}"
        end
    end
end

to_update.each do |service, posts|
    posts.each do |post|
        begin
            url = send "update_on_#{service}", post
            status[post.name][service]["url"] = url
            status[post.name][service]["sha256"] = post.sha
        rescue
            puts "Failed to update '#{post.name}' on #{SERVICES[service]}"
        end
    end
end

save_status status
