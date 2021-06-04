from django.shortcuts import render, HttpResponseRedirect
from django import template
from .forms import UploadFileForm
import os.path
import os
from subprocess import Popen, PIPE
import uuid
import time


def index(request):
    return render(request, "index.html")


def show_file(request):
    """Handles the form after submission
    """
    st_time = time.time()

    global file_content

    file_content = ''
    if request.method == 'POST':
        checkbox = request.POST.get('checkbox')
        if checkbox is not None and checkbox == 'on':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES['file']
                for chunk in f.chunks():
                    file_content += chunk.decode('utf-8')
        else:
            file_content = request.POST['textcontent']

        temp_suffix = str(uuid.uuid4())
        content_file = 'data/temp_content_%s' % temp_suffix
        segment_file = 'data/temp_segment_%s' % temp_suffix
        headline_file = 'data/temp_headline_%s' % temp_suffix

        f_content = open(content_file, "w", encoding='utf-8')
        f_content.write(file_content)
        f_content.close()

        # content_file = 'data/sample.txt'

        # python path for aws
        # p1 = Popen(["/home/ubuntu/venv/bin/python", "toc_web/toc_engine/segment_generator.py", content_file, segment_file], cwd=".", stdout=PIPE, stderr=PIPE)

        p1 = Popen(["python", "toc_web/toc_engine/segment_generator.py", content_file, segment_file], cwd=".",
                   stdout=PIPE, stderr=PIPE)
        out1, err1 = p1.communicate()

        # debug print. remove if not needed
        # print(out1.decode('utf-8'))
        # print(err1.decode('utf-8'))

        # python path for aws
        # p2 = Popen(["/home/ubuntu/venv/bin/python", "toc_web/toc_engine/headline_generator.py", segment_file, headline_file], cwd=".", stdout=PIPE, stderr=PIPE)

        p2 = Popen(["python", "toc_web/toc_engine/headline_generator.py", segment_file, headline_file], cwd=".",
                   stdout=PIPE, stderr=PIPE)
        out2, err2 = p2.communicate()

        # debug print. remove if not needed
        # print(out2.decode('utf-8'))
        # print(err2.decode('utf-8'))

        # now read genearted headline file to populate titles and segment lists
        f_headline = open(headline_file, "r", encoding='utf-8')
        titles = []
        segments = []
        title = ""
        segment = ""
        is_title = False
        for line in f_headline:
            if "-----" in line:
                if title != "" and segment != "":
                    titles.append(title.replace("\n", ""))
                    segments.append(segment.replace("\n", ""))

                    title = ""
                    segment = ""

                is_title = True
                continue
            else:
                if is_title:
                    title = line
                    is_title = False
                else:
                    segment += line

        # now see if there is any segment data yet to be added
        if title != "" and segment != "":
            titles.append(title.replace("\n", ""))
            segments.append(segment.replace("\n", ""))

        f_headline.close()
        # delete all temp files
        os.remove(content_file)
        os.remove(segment_file)
        os.remove(headline_file)

        # now render content for html
        result_content = list()
        for k in range(len(titles)):
            result_content.append(
                {
                    "title": titles[k],
                    "content": segments[k]
                }
            )
        # print(result_content)

        marked_file_contents = handle_file_contents(result_content)
        list_items = generate_list(result_content)
        context = {'file_content': marked_file_contents, 'list_items': list_items}

        print("Ended...{}s".format(time.time() - st_time))

        return render(request, "showFile.html", context)


def handle_file_contents(result_content):
    """Marks the list items present in result_content by converting the
    titles into H1 tags
    """
    new_contents = '<div id="file-content">'
    section_count = 0
    for content in result_content:
        section_count += 1
        for key, value in content.items():
            if key == 'title':
                new_contents += f'<h1 id="section_{section_count}">{value}</h1>'
            else:
                new_contents += value
    # for content in result_content:
    #     for key, value in content.items():
    #         if key == 'title':
    #             new_contents = new_contents.replace(value, f'<h1 id="{value}">{value}</h1>', 1)
    new_contents += '</div>'
    return new_contents


def generate_list(result_content):
    """Generates the item view list
    """
    list_items = ''
    section_count = 0
    for content in result_content:
        section_count += 1
        for key, value in content.items():
            if key == 'title':
                list_items += f'<li class="nav-item"> \
                    <a class="nav-link link" name="section_{section_count}" href="#section_{section_count}"> \
                    <span data-feather="file"></span> \
                    {value} <span class="sr-only"></span> \
                    </a> \
                </li>'
    return list_items
